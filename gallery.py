import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

def open_gallery():
    folder_path = filedialog.askdirectory()
    for widget in frame.winfo_children():
        widget.destroy()
    for img_file in os.listdir(folder_path):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(os.path.join(folder_path, img_file))
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=img)
            label.image = img  # keep a reference!
            label.pack(side='left', padx=5)

root = tk.Tk()
root.title("Image Gallery")
btn = tk.Button(root, text="Open Folder", command=open_gallery)
btn.pack()
frame = tk.Frame(root)
frame.pack()
root.mainloop()
