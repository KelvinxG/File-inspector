import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import plotly.graph_objects as go



def get_size_in_mb(size_in_bytes):
    """Converts size from bytes to MB."""
    return size_in_bytes / (1024 * 1024)

def get_size_in_gb(size_in_bytes):
    """Converts size from bytes to GB."""
    return size_in_bytes / (1024 * 1024 * 1024)


def calculate_folder_size(folder_path):
    """Calculate the total size of all accessible files in the given folder."""
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(file_path)
            except Exception:
                # Ignore files that cannot be accessed
                pass
    return total_size

def generate_pie_chart(folder_labels, folder_sizes_mb, use_plotly=False, root_dir=""):
    """Generates a pie chart using either Matplotlib or Plotly."""
    if use_plotly:
        # Create interactive pie chart using Plotly
        hover_texts = []
        for label, size in zip(folder_labels, folder_sizes_mb):
            if size >= 1024:  # Size in GB
                hover_texts.append(f"{label}: {size/1024:.2f} GB")
            else:  # Size in MB
                hover_texts.append(f"{label}: {size:.2f} MB")
        
        fig = go.Figure(data=[go.Pie(labels=folder_labels, values=folder_sizes_mb, hovertext=hover_texts, hoverinfo="label+percent+text")])
        fig.update_traces(textinfo='percent', textposition='inside')
        fig.update_layout(title_text=f"Disk Usage by Folder in {root_dir}")
        fig.show()
    else:
        # Create static pie chart using Matplotlib
        plt.figure(figsize=(10, 7))
        plt.pie(folder_sizes_mb, labels=folder_labels, autopct='%1.1f%%', startangle=140)
        plt.title(f"Disk Usage by Folder in {root_dir}")
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.show()

def inspect_parent_folders(root_dir, use_plotly=False):
    """Calculate the total size of each parent folder and display it with a pie chart."""
    folder_sizes = {}
    with ThreadPoolExecutor() as executor:
        future_to_folder = {
            executor.submit(calculate_folder_size, os.path.join(root_dir, item)): item
            for item in os.listdir(root_dir)
            if os.path.isdir(os.path.join(root_dir, item))
        }
        for future in as_completed(future_to_folder):
            folder = future_to_folder[future]
            try:
                total_size = future.result()
                folder_sizes[folder] = total_size
            except Exception as e:
                print(f"Could not calculate size for folder {folder}. Error: {e}")

    # Prepare data for pie chart
    folder_labels = []
    folder_sizes_mb = []
    for folder, size in folder_sizes.items():
        size_in_gb = get_size_in_gb(size)
        size_in_mb = get_size_in_mb(size)
        if size_in_gb >= 1:
            folder_labels.append(f"{folder} ({size_in_gb:.2f} GB)")
            folder_sizes_mb.append(size_in_gb * 1024)  # Convert GB back to MB for relative sizing
        else:
            folder_labels.append(f"{folder} ({size_in_mb:.2f} MB)")
            folder_sizes_mb.append(size_in_mb)

    # Generate pie chart
    generate_pie_chart(folder_labels, folder_sizes_mb, use_plotly, root_dir)


if __name__ == "__main__":
    root_directory = os.getcwd()
    inspect_parent_folders(root_directory,use_plotly=False)
