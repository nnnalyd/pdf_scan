import tkinter as tk
from tkinter import messagebox, filedialog
import os

def submit():
    global file_path, excel_path
    file_path = file_entry.get()
    excel_path = excel_entry.get()
    
    if not os.path.isdir(file_path):
        messagebox.showerror("Error", "Please select a valid folder.")
        return

    messagebox.showinfo("Customer Name", f"Selected Folder: {file_path}")
    root.quit()


def browse_file():
    folder_path = filedialog.askdirectory()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, folder_path)

def browse_excel():
    excel_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    excel_entry.delete(0, tk.END)
    excel_entry.insert(0, excel_path)

# Create the main window
root = tk.Tk()
root.title("Customer Name and PDF Input")
root.geometry("600x400")

# Create a file input label and entry
file_label = tk.Label(root, text="Select a folder:")
file_label.pack(pady=5)
file_entry = tk.Entry(root, width=40)
file_entry.pack(pady=5)
# Create a browse button
browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=5)

excel_label = tk.Label(root, text="Select an output excel file:")
excel_label.pack(pady=5)
excel_entry = tk.Entry(root, width=40)
excel_entry.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=browse_excel)
browse_button.pack(pady=5)

# Create a submit button
submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.pack(pady=10)

# Run the main loop
root.mainloop()

# Return values for use in another Python file
def get_customer_details():
    return file_path, excel_path
