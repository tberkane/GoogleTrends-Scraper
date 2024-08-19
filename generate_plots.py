import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


def generate_lineplot(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path, parse_dates=["date"])

    # Get the name of the second column (assumes it's the data column)
    data_column = df.columns[1]

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(df["date"], df[data_column])

    # Customize the plot
    plt.title(f"{os.path.basename(file_path)} - {data_column}")
    plt.xlabel("Date")
    plt.ylabel(data_column)
    plt.xticks(rotation=45)

    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    plt.gcf().autofmt_xdate()  # Rotation

    # Adjust layout and save the plot
    plt.tight_layout()
    output_file = f"/home/thomas/Documents/bch/GoogleTrends-Scraper/plots/{os.path.basename(file_path).replace('.csv', '.png')}"
    plt.savefig(output_file)
    plt.close()  # Close the plot to free up memory

    return output_file


def process_csv_files(directory):
    generated_plots = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            output_file = f"/home/thomas/Documents/bch/GoogleTrends-Scraper/plots/{filename.replace('.csv', '.png')}"
            if not os.path.exists(output_file):
                try:
                    plot_file = generate_lineplot(file_path)
                    generated_plots.append(plot_file)
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
    return generated_plots


# Directory path
results_dir = "results/"

# Generate plots for CSV files and get the list of generated plot files
generated_plots = process_csv_files(results_dir)

# Print the results
if generated_plots:
    print(f"Generated {len(generated_plots)} plots:")
    for plot in generated_plots:
        print(f"- {plot}")
else:
    print("No new plots were generated.")
