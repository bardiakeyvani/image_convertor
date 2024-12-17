import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import pillow_heif
import os
import sys
from pathlib import Path
import threading
import queue

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()


class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to JPEG Converter")
        self.root.geometry("600x500")

        # Selected path variable
        self.selected_path = tk.StringVar()

        # Message queue for thread communication
        self.message_queue = queue.Queue()

        self.create_widgets()
        self.check_queue()

    def update_quality_info(self, *args):
        """Update the quality information label based on slider value"""
        quality = self.quality_var.get()
        size_impact = ""

        if quality >= 90:
            size_impact = "Largest file size, best quality"
        elif quality >= 70:
            size_impact = "Good balance of size and quality"
        elif quality >= 50:
            size_impact = "Smaller files, acceptable quality"
        else:
            size_impact = "Smallest files, reduced quality"

        self.quality_info.config(text=f"Quality: {quality}%\n{size_impact}")

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Title
        title_label = tk.Label(
            main_frame,
            text="Image to JPEG Converter (HEIC supported)",
            font=("Helvetica", 16, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Path display
        path_frame = tk.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 20))

        path_label = tk.Label(
            path_frame, textvariable=self.selected_path, wraplength=500, justify="left"
        )
        path_label.pack(side="left", fill="x", expand=True)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)

        self.browse_file_button = tk.Button(
            button_frame, text="Select File", command=self.browse_file, width=15
        )
        self.browse_file_button.pack(side="left", padx=5)

        self.browse_dir_button = tk.Button(
            button_frame, text="Select Folder", command=self.browse_directory, width=15
        )
        self.browse_dir_button.pack(side="left", padx=5)

        self.convert_button = tk.Button(
            button_frame, text="Convert", command=self.start_conversion, width=15
        )
        self.convert_button.pack(side="left", padx=5)

        # Quality control frame
        quality_frame = tk.LabelFrame(main_frame, text="JPEG Quality", padx=10, pady=10)
        quality_frame.pack(fill="x", pady=(0, 20))

        # Quality slider
        self.quality_var = tk.IntVar(value=95)
        self.quality_slider = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.quality_var,
            command=self.update_quality_info,
        )
        self.quality_slider.pack(fill="x", pady=(0, 5))

        # Quality info label
        self.quality_info = tk.Label(
            quality_frame,
            text="Higher quality = Larger file size\nCurrent: 95% (Recommended)",
            justify=tk.CENTER,
        )
        self.quality_info.pack()

        # Status frame
        self.status_label = tk.Label(
            main_frame, text="", wraplength=500, justify="left"
        )
        self.status_label.pack(pady=20)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x", pady=(0, 20))

        # Status bar
        self.status_bar = tk.Label(
            self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def check_queue(self):
        """Check for messages from the conversion thread"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                msg_type = msg.get("type", "")

                if msg_type == "status":
                    self.status_bar.config(text=msg["text"])
                elif msg_type == "progress":
                    self.progress_var.set(msg["value"])
                elif msg_type == "complete":
                    self.status_label.config(text=msg["text"])
                    self.enable_buttons()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def enable_buttons(self):
        """Enable the buttons after conversion is complete"""
        self.browse_file_button.config(state=tk.NORMAL)
        self.browse_dir_button.config(state=tk.NORMAL)
        self.convert_button.config(state=tk.NORMAL)

    def disable_buttons(self):
        """Disable the buttons during conversion"""
        self.browse_file_button.config(state=tk.DISABLED)
        self.browse_dir_button.config(state=tk.DISABLED)
        self.convert_button.config(state=tk.DISABLED)

    def browse_file(self):
        """Open file dialog to select an image file"""
        path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=[
                ("Image files", "*.png *.bmp *.gif *.tiff *.webp *.heic *.HEIC"),
                ("All files", "*.*"),
            ],
        )
        if path:  # If a file was selected
            self.selected_path.set(path)
            self.status_label.config(text="")
            self.progress_var.set(0)
            self.status_bar.config(text="Ready")

    def browse_directory(self):
        """Open directory dialog to select a folder"""
        path = filedialog.askdirectory(title="Select a folder")
        if path:  # If a directory was selected
            self.selected_path.set(path)
            self.status_label.config(text="")
            self.progress_var.set(0)
            self.status_bar.config(text="Ready")

    def is_heic_file(self, file_path):
        """Check if the file is a HEIC image"""
        return file_path.lower().endswith((".heic"))

    def convert_single_image(self, image_path):
        """Convert a single image to JPEG"""
        try:
            # Get output path (before opening the image)
            output_path = os.path.splitext(image_path)[0] + ".jpg"

            # Update status
            self.message_queue.put(
                {
                    "type": "status",
                    "text": f"Converting: {os.path.basename(image_path)}",
                }
            )

            # Open and process the image
            img = Image.open(image_path)

            # Convert to RGB if necessary (required for JPEG)
            if img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            ):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(
                    img, mask=img.split()[-1] if img.mode == "RGBA" else None
                )
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Get the current quality setting
            quality = self.quality_var.get()

            # Save as JPEG with selected quality
            img.save(output_path, "JPEG", quality=quality)
            return True

        except Exception as e:
            print(f"Error converting {image_path}: {str(e)}")  # For debugging
            return False

    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        self.disable_buttons()
        self.progress_var.set(0)
        thread = threading.Thread(target=self.convert)
        thread.daemon = True
        thread.start()

    def convert(self):
        """Handle conversion of selected path"""
        path = self.selected_path.get()

        if not path:
            messagebox.showwarning(
                "Warning", "Please select a file or directory first!"
            )
            self.enable_buttons()
            return

        if os.path.isfile(path):
            # Single file conversion
            self.message_queue.put({"type": "progress", "value": 0})

            if self.convert_single_image(path):
                self.message_queue.put(
                    {
                        "type": "complete",
                        "text": f"Successfully converted: {os.path.basename(path)}",
                    }
                )
                self.message_queue.put({"type": "progress", "value": 100})
                self.message_queue.put(
                    {"type": "status", "text": "Conversion complete"}
                )
            else:
                self.message_queue.put(
                    {
                        "type": "complete",
                        "text": f"Failed to convert: {os.path.basename(path)}",
                    }
                )
                self.message_queue.put({"type": "status", "text": "Conversion failed"})

        elif os.path.isdir(path):
            # Directory conversion
            success_count = 0
            fail_count = 0

            # Count total files for progress bar
            total_files = sum(
                1
                for _, _, files in os.walk(path)
                for file in files
                if file.lower().endswith(
                    (".png", ".bmp", ".gif", ".tiff", ".webp", ".heic")
                )
            )

            if total_files == 0:
                self.message_queue.put(
                    {
                        "type": "complete",
                        "text": "No compatible images found in the directory",
                    }
                )
                self.message_queue.put({"type": "status", "text": "No images found"})
                self.enable_buttons()
                return

            processed_files = 0
            for root, _, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(
                        (".png", ".bmp", ".gif", ".tiff", ".webp", ".heic")
                    ):
                        full_path = os.path.join(root, file)
                        if self.convert_single_image(full_path):
                            success_count += 1
                        else:
                            fail_count += 1

                        processed_files += 1
                        progress = (processed_files / total_files) * 100
                        self.message_queue.put({"type": "progress", "value": progress})

            self.message_queue.put(
                {
                    "type": "complete",
                    "text": f"Conversion complete!\nSuccessfully converted: {success_count} files\nFailed: {fail_count} files",
                }
            )
            self.message_queue.put(
                {"type": "status", "text": "All conversions complete"}
            )

        else:
            messagebox.showerror("Error", "Selected path does not exist!")
            self.message_queue.put({"type": "status", "text": "Error: Invalid path"})
            self.enable_buttons()


def main():
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
