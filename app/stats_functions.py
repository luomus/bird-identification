
import pandas as pd
import matplotlib.pyplot as plt
import os

from typing import Optional

def generate_histograms(df: pd.DataFrame, threshold: float, output_directory: str) -> bool:
    """
    Generates histograms for each species in a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the data.
    - threshold (float): The threshold value used to filter rows.
    - output_directory (str): The directory to save the histograms.

    Returns:
    - int: The number of histograms generated.
    """

    print("Generating histograms")

    BUCKETS = 100

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

        print(f"Generated histogram for {species}")

    return True


def generate_temporal_chart(df: pd.DataFrame, output_directory: str) -> bool:
    """
    Loops through each species in a DataFrame and generates bar charts of counts of rows in one-hour time buckets.

    Parameters:
    - df (pandas.DataFrame): The input dataframe with 'Timestamp' and 'Scientific name'.
    """

    # Ensure Timestamp is a datetime object
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Get the unique scientific names
    species_list = df['Scientific name'].unique()
    
    # Loop through each species
    for species in species_list:
        # Filter the dataframe for the current species
        species_df = df[df['Scientific name'] == species].copy()
        
        # Group by one-hour time buckets
        species_df.loc[:, 'Hour'] = species_df['Timestamp'].dt.floor('h')
        hourly_counts = species_df.groupby('Hour').size()

        # Plot the bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(hourly_counts.index, hourly_counts.values, width=0.03, color='orange')
        plt.title(f"Observation Counts for {species}")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the figure
        file_path = os.path.join(output_directory, f"{species.replace(' ', '_')}_temporal.png")
        plt.savefig(file_path)
        plt.close()

        print(f"Generated temporal chart for {species}")

    return True
