import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math
import re
from collections import Counter
import datetime

class LegoMosaicGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Lego Mosaic Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Constants
        self.LEGO_WIDTH = 0.314961  # Width of a 1x1 Lego brick in inches
        self.MAX_LENGTH = 30  # Maximum length in inches
        self.MAX_LEGO_PIECES = int(self.MAX_LENGTH / self.LEGO_WIDTH)  # Maximum number of Lego pieces in one dimension
        self.GRID_SIZE = 10  # Size of grid for instructions (10x10)
        
        # Load Lego colors
        self.load_lego_colors()
        
        # Create GUI
        self.create_gui()
        
        # Variables
        self.original_image = None
        self.mosaic_image = None
        self.brick_counts = {}
        self.brick_colors = {}
        
    def load_lego_colors(self):
        """Load Lego colors from Excel file"""
        try:
            df = pd.read_excel("Lego Colors.xlsx")
            
            # Extract RGB values from the RGB column
            self.lego_colors = []
            self.lego_color_names = []
            
            for _, row in df.iterrows():
                # Extract RGB values using regex
                rgb_str = row['RGB']
                # Remove parentheses and split by comma
                rgb_values = rgb_str.strip("()").split(',')
                if len(rgb_values) == 3:
                    try:
                        r = int(rgb_values[0].strip())
                        g = int(rgb_values[1].strip())
                        b = int(rgb_values[2].strip())
                        self.lego_colors.append((r, g, b))
                        self.lego_color_names.append(row['Color'])
                    except ValueError:
                        print(f"Error parsing RGB values: {rgb_str}")
                        continue
            
            print(f"Loaded {len(self.lego_colors)} Lego colors")
        except Exception as e:
            print(f"Error loading Lego colors: {e}")
            messagebox.showerror("Error", f"Failed to load Lego colors: {e}")
            self.lego_colors = []
            self.lego_color_names = []
    
    def create_gui(self):
        """Create the GUI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top panel - File selection
        top_frame = ttk.LabelFrame(main_frame, text="Image Selection")
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Image file:").grid(row=0, column=0, padx=5, pady=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.file_path_var, width=70).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(top_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(top_frame, text="Generate Mosaic", command=self.generate_mosaic).grid(row=0, column=3, padx=5, pady=5)
        
        # Middle panel - Images
        images_frame = ttk.Frame(main_frame)
        images_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Original image panel
        original_frame = ttk.LabelFrame(images_frame, text="Original Image")
        original_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.original_image_label = ttk.Label(original_frame)
        self.original_image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mosaic image panel
        mosaic_frame = ttk.LabelFrame(images_frame, text="Lego Mosaic")
        mosaic_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.mosaic_image_label = ttk.Label(mosaic_frame)
        self.mosaic_image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set weight for the columns
        images_frame.columnconfigure(0, weight=1)
        images_frame.columnconfigure(1, weight=1)
        
        # Bottom panel - Brick information
        info_frame = ttk.LabelFrame(main_frame, text="Lego Brick Information")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Brick count text with scrollbar
        brick_count_frame = ttk.Frame(info_frame)
        brick_count_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.brick_count_text = tk.Text(brick_count_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(brick_count_frame, command=self.brick_count_text.yview)
        self.brick_count_text.configure(yscrollcommand=scrollbar.set)
        
        self.brick_count_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button to download instructions
        self.download_btn = ttk.Button(main_frame, text="Download Building Instructions", 
                                      command=self.generate_instructions, state=tk.DISABLED)
        self.download_btn.pack(pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_file(self):
        """Open file dialog to select an image"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set(f"Selected file: {os.path.basename(file_path)}")
            self.load_original_image(file_path)
    
    def load_original_image(self, file_path):
        """Load and display the original image"""
        try:
            self.original_image = Image.open(file_path)
            self.display_image(self.original_image, self.original_image_label, max_size=400)
            self.status_var.set(f"Loaded image: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.status_var.set("Error loading image")
    
    def display_image(self, image, label, max_size=400):
        """Display an image on a label, resized to fit within max_size"""
        if image:
            # Calculate new size to fit within max_size while maintaining aspect ratio
            width, height = image.size
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            # Resize image for display only
            display_image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(display_image)
            label.configure(image=photo)
            label.image = photo  # Keep a reference to prevent garbage collection
    
    def generate_mosaic(self):
        """Generate the Lego mosaic from the original image"""
        if not self.original_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            self.status_var.set("Generating mosaic...")
            
            # Get original image dimensions
            width, height = self.original_image.size
            
            # Calculate the resize factor based on the maximum Lego size constraint
            resize_factor = self.calculate_resize_factor(width, height)
            
            # Calculate new dimensions
            width_reduced = int(width / resize_factor)
            height_reduced = int(height / resize_factor)
            
            # Resize the image (pixelize)
            resized_img = self.original_image.resize((width_reduced, height_reduced), Image.NEAREST)
            
            # Convert to Lego colors
            lego_img = self.convert_to_lego_colors(resized_img)
            
            # Save mosaic image
            self.mosaic_image = lego_img
            
            # Display the mosaic image
            self.display_image(lego_img, self.mosaic_image_label, max_size=400)
            
            # Calculate and display brick information
            self.display_brick_info(width_reduced, height_reduced)
            
            # Enable the download instructions button
            self.download_btn.config(state=tk.NORMAL)
            
            # Update status
            self.status_var.set(f"Mosaic generated: {width_reduced}x{height_reduced} pieces")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate mosaic: {e}")
            self.status_var.set("Error generating mosaic")
    
    def calculate_resize_factor(self, width, height):
        """Calculate the resize factor based on the maximum physical size constraint"""
        # Calculate how many Lego pieces would fit in the max length
        width_in_lego = width / self.MAX_LEGO_PIECES
        height_in_lego = height / self.MAX_LEGO_PIECES
        
        # Use the larger dimension to determine resize factor
        resize_factor = max(width_in_lego, height_in_lego)
        
        # Ensure we have at least a factor of 1
        return max(1, resize_factor)
    
    def convert_to_lego_colors(self, image):
        """Convert the image to use only Lego colors"""
        if not self.lego_colors:
            messagebox.showwarning("Warning", "No Lego colors loaded")
            return image
        
        # Create a new image with the same size
        lego_image = Image.new("RGB", image.size)
        
        # Convert image to RGB mode if it's not already
        image = image.convert("RGB")
        
        # Prepare a dictionary to count bricks by color
        self.brick_counts = Counter()
        self.brick_colors = {}
        
        # Process each pixel
        for y in range(image.height):
            for x in range(image.width):
                # Get the RGB values of the pixel
                r, g, b = image.getpixel((x, y))
                
                # Find the closest Lego color
                closest_color_idx = self.find_closest_color((r, g, b))
                
                # Get the closest color
                lego_color = self.lego_colors[closest_color_idx]
                color_name = self.lego_color_names[closest_color_idx]
                
                # Set the pixel to the Lego color
                lego_image.putpixel((x, y), lego_color)
                
                # Count this brick
                self.brick_counts[color_name] += 1
                self.brick_colors[color_name] = lego_color
        
        return lego_image
    
    def find_closest_color(self, rgb):
        """Find the index of the closest Lego color to the given RGB value"""
        r, g, b = rgb
        min_distance = float('inf')
        closest_idx = 0
        
        for i, (lr, lg, lb) in enumerate(self.lego_colors):
            # Calculate Euclidean distance in RGB space
            distance = math.sqrt((r - lr)**2 + (g - lg)**2 + (b - lb)**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_idx = i
        
        return closest_idx
    
    def display_brick_info(self, width, height):
        """Display information about the required Lego bricks"""
        # Clear the text widget
        self.brick_count_text.delete('1.0', tk.END)
        
        # Add header information
        self.brick_count_text.insert(tk.END, f"Original Image Size: {self.original_image.size[0]}x{self.original_image.size[1]} pixels\n")
        self.brick_count_text.insert(tk.END, f"Mosaic Size: {width}x{height} bricks\n")
        self.brick_count_text.insert(tk.END, f"Total Bricks Required: {width * height}\n")
        self.brick_count_text.insert(tk.END, f"Physical Size: {width * self.LEGO_WIDTH:.2f}\" x {height * self.LEGO_WIDTH:.2f}\"\n\n")
        
        # Add brick count by color
        self.brick_count_text.insert(tk.END, "Lego Bricks Required by Color:\n")
        self.brick_count_text.insert(tk.END, "================================\n")
        
        # Sort by count (descending)
        for color_name, count in sorted(self.brick_counts.items(), key=lambda x: x[1], reverse=True):
            # Get RGB values
            if color_name in self.brick_colors:
                r, g, b = self.brick_colors[color_name]
                # Convert to hex
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                
                # Insert color information with tag
                tag_name = f"color_{color_name.replace(' ', '_')}"
                self.brick_count_text.insert(tk.END, f"{color_name}: ", tag_name)
                self.brick_count_text.insert(tk.END, f"{count} bricks (RGB: {r},{g},{b} Hex: {hex_color})\n")
                
                # Configure tag with background color similar to the Lego color
                self.brick_count_text.tag_configure(tag_name, background=hex_color, foreground=self.get_contrasting_text_color(r, g, b))

    def get_contrasting_text_color(self, r, g, b):
        """Determine whether to use black or white text based on the background color"""
        # Use luminance formula to determine if color is light or dark
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return 'black' if luminance > 128 else 'white'
    
    def generate_instructions(self):
        """Generate building instructions for the Lego mosaic"""
        if not self.mosaic_image:
            messagebox.showwarning("Warning", "Please generate a mosaic first")
            return
        
        try:
            # Ask user where to save the instructions
            output_dir = filedialog.askdirectory(title="Select folder to save building instructions")
            if not output_dir:
                return  # User cancelled
            
            self.status_var.set("Generating building instructions...")
            
            # Create a directory for the instructions with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            instructions_dir = os.path.join(output_dir, f"Lego_Instructions_{timestamp}")
            os.makedirs(instructions_dir, exist_ok=True)
            
            # Create an overview image of the full mosaic with grid
            self.create_overview_image(instructions_dir)
            
            # Create the grid-based instruction images
            self.create_grid_instructions(instructions_dir)
            
            # Create a summary text file
            self.create_summary_file(instructions_dir)
            
            # Success message
            messagebox.showinfo("Instructions Generated", 
                               f"Building instructions have been saved to:\n{instructions_dir}")
            
            self.status_var.set("Building instructions generated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate instructions: {e}")
            self.status_var.set("Error generating instructions")
    
    def create_overview_image(self, output_dir):
        """Create an overview image of the full mosaic with grid lines"""
        # Get dimensions
        width, height = self.mosaic_image.size
        
        # Create a larger version for better visibility
        scale_factor = 20  # Each Lego pixel will be 20x20 pixels
        overview_img = Image.new("RGB", (width * scale_factor, height * scale_factor), color="white")
        draw = ImageDraw.Draw(overview_img)
        
        # Draw the mosaic
        for y in range(height):
            for x in range(width):
                pixel_color = self.mosaic_image.getpixel((x, y))
                draw.rectangle([x * scale_factor, y * scale_factor, 
                               (x+1) * scale_factor - 1, (y+1) * scale_factor - 1], 
                               fill=pixel_color)
        
        # Draw the grid
        grid_color = (200, 200, 200)  # Light gray
        
        # Draw horizontal grid lines
        for y in range(0, height + 1):
            if y % self.GRID_SIZE == 0:  # Major grid line (every 10)
                line_color = (0, 0, 0)  # Black
                line_width = 2
            else:
                line_color = grid_color
                line_width = 1
            draw.line([(0, y * scale_factor), (width * scale_factor, y * scale_factor)], 
                     fill=line_color, width=line_width)
        
        # Draw vertical grid lines
        for x in range(0, width + 1):
            if x % self.GRID_SIZE == 0:  # Major grid line (every 10)
                line_color = (0, 0, 0)  # Black
                line_width = 2
            else:
                line_color = grid_color
                line_width = 1
            draw.line([(x * scale_factor, 0), (x * scale_factor, height * scale_factor)], 
                     fill=line_color, width=line_width)
        
        # Add section labels (A1, A2, B1, B2, etc.)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Label each 10x10 section
        for grid_y in range(0, height, self.GRID_SIZE):
            row_label = chr(65 + grid_y // self.GRID_SIZE)  # A, B, C...
            for grid_x in range(0, width, self.GRID_SIZE):
                col_label = str(1 + grid_x // self.GRID_SIZE)  # 1, 2, 3...
                grid_label = f"{row_label}{col_label}"
                
                # Calculate the center position of the grid
                text_pos = (grid_x * scale_factor + 5, grid_y * scale_factor + 5)
                
                # Draw white background for text
                text_bbox = draw.textbbox(text_pos, grid_label, font=font)
                draw.rectangle(text_bbox, fill=(255, 255, 255, 180))
                
                # Draw the label
                draw.text(text_pos, grid_label, fill=(0, 0, 0), font=font)
        
        # Save the overview image
        overview_path = os.path.join(output_dir, "00_Full_Mosaic_Overview.png")
        overview_img.save(overview_path)
    
    def create_grid_instructions(self, output_dir):
        """Create instruction images for each 10x10 grid section"""
        width, height = self.mosaic_image.size
        
        # Calculate how many grid sections we'll have
        grid_cols = math.ceil(width / self.GRID_SIZE)
        grid_rows = math.ceil(height / self.GRID_SIZE)
        
        # Define the scale for the enlarged grid sections
        scale_factor = 50  # Each Lego pixel will be 50x50 pixels
        
        # Process each grid section
        for grid_row in range(grid_rows):
            row_label = chr(65 + grid_row)  # A, B, C...
            
            for grid_col in range(grid_cols):
                col_label = str(grid_col + 1)  # 1, 2, 3...
                grid_label = f"{row_label}{col_label}"
                
                # Calculate the boundaries of this grid section
                start_x = grid_col * self.GRID_SIZE
                start_y = grid_row * self.GRID_SIZE
                end_x = min(start_x + self.GRID_SIZE, width)
                end_y = min(start_y + self.GRID_SIZE, height)
                
                # Create an image for this grid section (with padding for labels)
                padding = 50
                grid_img = Image.new("RGB", 
                                    ((end_x - start_x) * scale_factor + 2 * padding, 
                                     (end_y - start_y) * scale_factor + 2 * padding), 
                                    color="white")
                draw = ImageDraw.Draw(grid_img)
                
                # Draw the grid section
                for y in range(start_y, end_y):
                    for x in range(start_x, end_x):
                        # Get the pixel color
                        pixel_color = self.mosaic_image.getpixel((x, y))
                        
                        # Calculate position in the enlarged grid
                        grid_pixel_x = (x - start_x) * scale_factor + padding
                        grid_pixel_y = (y - start_y) * scale_factor + padding
                        
                        # Draw the enlarged pixel
                        draw.rectangle([grid_pixel_x, grid_pixel_y, 
                                       grid_pixel_x + scale_factor - 1, 
                                       grid_pixel_y + scale_factor - 1], 
                                       fill=pixel_color)
                        
                        # Add coordinates inside each brick
                        position_label = f"{x+1},{y+1}"
                        try:
                            font = ImageFont.truetype("arial.ttf", 12)
                        except:
                            font = ImageFont.load_default()
                        
                        # Determine text color based on background
                        r, g, b = pixel_color
                        text_color = self.get_contrasting_text_color(r, g, b)
                        
                        # Calculate position for the text
                        text_x = grid_pixel_x + scale_factor // 2 - 10
                        text_y = grid_pixel_y + scale_factor // 2 - 6
                        
                        # Draw the position label
                        draw.text((text_x, text_y), position_label, fill=text_color, font=font)
                
                # Draw grid lines
                for x in range(start_x, end_x + 1):
                    line_x = (x - start_x) * scale_factor + padding
                    draw.line([(line_x, padding), 
                              (line_x, (end_y - start_y) * scale_factor + padding)], 
                             fill=(100, 100, 100), width=1)
                
                for y in range(start_y, end_y + 1):
                    line_y = (y - start_y) * scale_factor + padding
                    draw.line([(padding, line_y), 
                              ((end_x - start_x) * scale_factor + padding, line_y)], 
                             fill=(100, 100, 100), width=1)
                
                # Add section title
                title = f"Section {grid_label} ({start_x+1},{start_y+1}) to ({end_x},{end_y})"
                try:
                    title_font = ImageFont.truetype("arial.ttf", 24)
                except:
                    title_font = ImageFont.load_default()
                
                # Draw the title
                draw.text((padding, 10), title, fill=(0, 0, 0), font=title_font)
                
                # Save the grid section image
                section_path = os.path.join(output_dir, f"{grid_label}_Section.png")
                grid_img.save(section_path)
    
    def create_summary_file(self, output_dir):
        """Create a summary text file with brick information"""
        summary_path = os.path.join(output_dir, "Brick_Summary.txt")
        
        with open(summary_path, 'w') as f:
            # Write header
            f.write("LEGO MOSAIC BUILDING INSTRUCTIONS\n")
            f.write("===============================\n\n")
            
            # Write image information
            width, height = self.mosaic_image.size
            f.write(f"Original Image: {os.path.basename(self.file_path_var.get())}\n")
            f.write(f"Mosaic Size: {width}x{height} bricks\n")
            f.write(f"Total Bricks Required: {width * height}\n")
            f.write(f"Physical Size: {width * self.LEGO_WIDTH:.2f}\" x {height * self.LEGO_WIDTH:.2f}\"\n\n")
            
            # Write brick information
            f.write("BRICK REQUIREMENTS\n")
            f.write("=================\n\n")
            
            # Sort by count (descending)
            for color_name, count in sorted(self.brick_counts.items(), key=lambda x: x[1], reverse=True):
                # Get RGB values
                if color_name in self.brick_colors:
                    r, g, b = self.brick_colors[color_name]
                    # Convert to hex
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    f.write(f"{color_name}: {count} bricks (RGB: {r},{g},{b}  Hex: {hex_color})\n")
            
            # Write building instructions
            f.write("\n\nBUILDING INSTRUCTIONS\n")
            f.write("====================\n\n")
            f.write("1. Refer to the overview image (00_Full_Mosaic_Overview.png) to see the complete mosaic.\n")
            f.write("2. The mosaic is divided into 10x10 sections labeled with letters and numbers (A1, A2, B1, etc.).\n")
            f.write("3. Use the individual section images to place bricks one by one.\n")
            f.write("4. Each brick in the section images is labeled with its coordinates.\n")
            f.write("5. Start from the bottom-left corner and work your way up and to the right.\n\n")
            
            f.write("Happy building!\n")

def main():
    root = tk.Tk()
    app = LegoMosaicGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main() 