
import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_historgrams(df, threshold, output_directory):
    """
    Generate histograms for each species in the DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the data.
    - threshold (float): The threshold value used to filter rows.
    - output_directory (str): The directory to save the histograms.

    Returns:
    - int: The number of histograms generated.
    """

    print("Generating histograms")

    BUCKETS = 100

    i = 0
    for species, group in df.groupby("Scientific name"):
        plt.figure()
        plt.hist(group["Confidence"], bins=[i / BUCKETS for i in range(BUCKETS + 1)])
        plt.axvline(x=threshold, color='grey', linestyle='--', linewidth=1.5)
        plt.title(f"{species}")
        plt.grid(axis='y', alpha=0.75)

        # Use integers on the y-axis
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))

        # Use tight layout
        plt.tight_layout()

        # Save the figure
        file_path = os.path.join(output_directory, f"{species.replace(' ', '_')}.png")
        plt.savefig(file_path)
        plt.close()

        i += 1

    return i

    

