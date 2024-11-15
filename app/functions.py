import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import rasterio

# calibrate prediction
def calibrate(p, cal_table):
    return [1/(1+np.exp(-(cal_table[i, 0]+cal_table[i, 1]*pr))) for i, pr in enumerate(p)]

# adjust prediction based on time of the year and latitude
def adjust(p, cls, migr_table, lat, lon, day):
    # handle leap year with 366 days
    if day > 365:
        day = 365
    for j in range(len(p)): # loop through all species
        c = cls[j]        
        # Probability that species has migrated to Finland
        migr_c = migr_table[c, :]
        p_migr = np.min((norm.cdf(day, loc=migr_c[0]+migr_c[1]*lat, scale=migr_c[4]/2), 
              1-norm.cdf(day, loc=migr_c[2]+migr_c[3]*lat, scale=migr_c[5]/2)))
        
        # Probability that species occurs in given area
        with rasterio.open('Pred_adjustment/distribution_maps/'+ str(c)+ '_a.tif') as src:
            for value in src.sample([(lon, lat)]): 
                p_dist_a = value
        p_dist_a = p_dist_a[0]
        if np.isnan(p_dist_a): # if no information from given location, species is considered possible
            p_dist_a=1
        
        # Use additional map for given time of the year:
        p_dist_b = 0
        use_b = 0
        if(migr_c[6]<migr_c[7]):
            if((day>=migr_c[6]) & (day<=migr_c[7])):
                use_b = 1
        if(migr_c[6]>migr_c[7]):
            if((day>=migr_c[6]) or (day<=migr_c[7])):
                use_b = 1
        if use_b==1:
            with rasterio.open('Pred_adjustment/distribution_maps/'+ str(c)+ '_b.tif') as src:
                for value in src.sample([(lon, lat)]): 
                    p_dist_b = value
            p_dist_b = p_dist_b[0]
            if np.isnan(p_dist_b):
                p_dist_b=1

        # Adjustment based on probability of species being present
        p_pres = p_migr * (p_dist_a + (1-p_dist_a)*use_b*p_dist_b)
        q = np.minimum(0, np.log10(p_pres)+1)
        q = np.maximum(q, -10) # avoid -inf
        p[j] = (np.maximum(0, p[j]+q*0.25))/np.maximum(0.0001, (1+q*0.25))
    return p

# filter and sort predictions based on threshold
def top_preds(prediction, timestamps, threshold=0.5):
    # prediction: classification model output (max results), timestamp: timestamps from model, threshold: threshold for filtering (0-1)
    cls= [idx for idx, val in enumerate(prediction) if val > threshold]
    prediction = np.array(prediction)[cls]
    ts = np.array(timestamps)[cls]
    if len(cls)>0:
        prediction, cls, ts = map(list, zip(*sorted(zip(prediction, cls, ts), reverse=True)))
    else:
        prediction=[]
        cls = []
        ts = []
    return prediction, cls, ts

# filter predictions based on threshold
def threshold_filter(preds, timestamps, threshold=0.5):
    # prediction: classification model output (all results), timestamp: timestamps from model, threshold: threshold for filtering (0-1)
    arg_where = np.where(preds>threshold)
    prediction = preds[arg_where]
    cls = arg_where[1]
    ts = timestamps[arg_where[0]]
    return prediction, cls, ts

# pad too short signal with zeros
def pad(signal, x1, x2, target_len=3*48000, sr=48000):
    # signal: input audio signal, x1: starting point in seconds x2: ending point in seconds, 
    # target_len: target length for signal, sr: sampling rate
    sig_out = np.zeros(target_len) 
    sig_out[int(x1*sr):int(x2*sr)] = signal[int(x1*sr):int(x2*sr)]
    return sig_out

# split input signal to overlapping chunks
def split_signal(sig, rate, seconds, overlap):
    # sig: input_signal, rate: sampling rate, seconds: target length in seconds,
    # overlap: overlap of consecutive frames in seconds, minlen: m
    sig_splits = []
    for i in range(0, len(sig), int((seconds - overlap) * rate)):
        split = sig[i:i + int(seconds * rate)]
        if len(split) < int(seconds * rate): # pad if clip is too short
            split = pad(split, 0, len(split)/rate, target_len=int(seconds*rate), sr=rate)     
        sig_splits.append(split)
    return sig_splits

# visualize results of network training
def plot_results(history, val = True):
    # history: model history object, val: show validation results
    acc = history['binary_accuracy']
    loss = history['loss']
    if val:
        val_acc = history['val_binary_accuracy']
        val_loss = history['val_loss']
    epochs = range(1, len(acc) + 1)
    plt.plot(epochs, acc, 'bo', label='Training acc')
    if val:
        plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training (and validation) accuracy')
    plt.legend()
    plt.figure()
    plt.plot(epochs, loss, 'bo', label='Training loss')
    if val:
        plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training (and validation) loss')
    plt.legend()
    plt.show()
    