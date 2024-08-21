import os
from concurrent.futures import ThreadPoolExecutor, as_completed
# import matplotlib.pyplot as plt
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

def inspect_parent_folders(root_dir):
    """Calculate the total size of each parent folder and display it with an interactive pie chart."""
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
    hover_texts = []
    for folder, size in folder_sizes.items():
        size_in_gb = get_size_in_gb(size)
        size_in_mb = get_size_in_mb(size)
        if size_in_gb >= 1:
            folder_labels.append(folder)
            folder_sizes_mb.append(size_in_gb * 1024)  # Convert GB back to MB for relative sizing
            hover_texts.append(f"{folder}: {size_in_gb:.2f} GB")
        else:
            folder_labels.append(folder)
            folder_sizes_mb.append(size_in_mb)
            hover_texts.append(f"{folder}: {size_in_mb:.2f} MB")

    # Create interactive pie chart
    fig = go.Figure(data=[go.Pie(labels=folder_labels, values=folder_sizes_mb, hovertext=hover_texts, hoverinfo="label+percent+text")])
    fig.update_traces(textinfo='percent', textposition='inside')
    fig.update_layout(title_text=f"Disk Usage by Folder in {root_dir}")
    fig.show()

if __name__ == "__main__":
    root_directory = "D:\python"
    inspect_parent_folders(root_directory)
