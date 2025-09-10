#!/usr/bin/env python3
"""
Par Buddy GUI - Graphical User Interface for Par Buddy Group Generator

This GUI application provides a user-friendly interface for the par_buddy.py script,
allowing users to select CSV files, configure output options, and generate HTML reports
through a simple graphical interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import webbrowser
from pathlib import Path
import csv
import subprocess
import platform

# Import the existing par_buddy classes
from par_buddy import GroupGenerator, HTMLGenerator


class ParBuddyGUI:
    """Main GUI application for Par Buddy group generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Par Buddy - Random Group Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Maximize the window (cross-platform)
        self.maximize_window()
        
        # Set application icon
        self.set_app_icon()
        
        # Variables
        self.csv_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.use_seed = tk.BooleanVar()
        self.seed_value = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready to generate groups...")
        
        # Initialize GUI
        self.setup_gui()
        self.center_window()
    
    def maximize_window(self):
        """Maximize the window in a cross-platform way."""
        try:
            if platform.system() == 'Darwin':  # macOS
                # On macOS, manually set to screen size since -zoomed doesn't work
                self.root.update_idletasks()
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                # Account for macOS menu bar (typically 25-30 pixels)
                self.root.geometry(f"{screen_width}x{screen_height - 25}+0+25")
            elif platform.system() == 'Windows':  # Windows
                # On Windows, use state
                self.root.state('zoomed')
            else:  # Linux and others
                # On Linux, try state first, fallback to manual sizing
                try:
                    self.root.state('zoomed')
                except tk.TclError:
                    # If zoomed state is not supported, maximize manually
                    self.root.update_idletasks()
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        except Exception as e:
            # If maximization fails, just continue with default size
            print(f"Warning: Could not maximize window: {str(e)}")
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def set_app_icon(self):
        """Set the application icon for the taskbar and window."""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, 'par_buddy.png')
            
            # Check if the icon file exists
            if os.path.exists(icon_path):
                # Set the icon for the window
                photo = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, photo)
            else:
                # If icon file doesn't exist, try to use a default or skip silently
                print(f"Warning: Icon file not found at {icon_path}")
                
        except Exception as e:
            # If there's any error setting the icon, just continue without it
            print(f"Warning: Could not set application icon: {str(e)}")
    
    def setup_gui(self):
        """Set up the main GUI layout."""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏌️ Par Buddy - Random Group Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # CSV File Selection Section
        csv_frame = ttk.LabelFrame(main_frame, text="1. Select Player Data (CSV File)", padding="10")
        csv_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        csv_frame.columnconfigure(1, weight=1)
        
        ttk.Button(csv_frame, text="Browse CSV File", 
                  command=self.browse_csv_file).grid(row=0, column=0, padx=(0, 10))
        
        self.csv_path_label = ttk.Label(csv_frame, textvariable=self.csv_file_path, 
                                       foreground="blue", cursor="hand2")
        self.csv_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.csv_path_label.bind("<Button-1>", self.open_csv_file)
        
        # CSV Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text="CSV Data Preview", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        # Preview controls
        preview_controls = ttk.Frame(preview_frame)
        preview_controls.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(preview_controls, text="Double-click any cell to edit. Right-click for options.").grid(row=0, column=0, sticky=tk.W)
        
        self.save_csv_button = ttk.Button(preview_controls, text="💾 Save Changes to CSV", 
                                         command=self.save_csv_changes, state='disabled')
        self.save_csv_button.grid(row=0, column=1, padx=(10, 0))
        
        # Treeview for CSV preview
        self.tree = ttk.Treeview(preview_frame, columns=('Name', 'Ranking', 'Gender', 'Playing'), 
                                show='headings', height=8)
        self.tree.heading('Name', text='Player Name')
        self.tree.heading('Ranking', text='Ranking')
        self.tree.heading('Gender', text='Gender')
        self.tree.heading('Playing', text='Playing')
        
        self.tree.column('Name', width=180)
        self.tree.column('Ranking', width=70, anchor='center')
        self.tree.column('Gender', width=70, anchor='center')
        self.tree.column('Playing', width=70, anchor='center')
        
        # Bind events for editing
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)  # Right-click context menu
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Variables for editing
        self.csv_data = []
        self.csv_headers = []
        self.has_unsaved_changes = False
        
        # Output File Section
        output_frame = ttk.LabelFrame(main_frame, text="2. Output HTML File", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Button(output_frame, text="Save HTML As", 
                  command=self.browse_output_file).grid(row=0, column=0, padx=(0, 10))
        
        self.output_path_label = ttk.Label(output_frame, textvariable=self.output_file_path, 
                                          foreground="blue")
        self.output_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="3. Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        seed_check = ttk.Checkbutton(options_frame, text="Use random seed for reproducible results", 
                                    variable=self.use_seed, command=self.toggle_seed)
        seed_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        seed_frame = ttk.Frame(options_frame)
        seed_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(seed_frame, text="Seed value:").grid(row=0, column=0, padx=(20, 5))
        self.seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_value, width=10, state='disabled')
        self.seed_entry.grid(row=0, column=1)
        
        # Generate Button
        generate_frame = ttk.Frame(main_frame)
        generate_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.generate_button = ttk.Button(generate_frame, text="🎲 Generate Random Groups", 
                                         command=self.generate_groups, style='Accent.TButton')
        self.generate_button.pack(pady=10)
        
        # Configure accent button style
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
        
        # Progress bar
        self.progress = ttk.Progressbar(generate_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status and Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Status & Results", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        results_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(results_frame, textvariable=self.status_text, 
                                     font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results text area
        self.results_text = tk.Text(results_frame, height=6, wrap=tk.WORD, 
                                   font=('Courier', 9), state='disabled')
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                         command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Open HTML button
        self.open_html_button = ttk.Button(results_frame, text="📄 Open HTML Report", 
                                          command=self.open_html_file, state='disabled')
        self.open_html_button.grid(row=2, column=0, pady=(10, 0))
        
        # Configure row weights for resizing
        main_frame.rowconfigure(2, weight=1)
        results_frame.rowconfigure(1, weight=1)
    
    def toggle_seed(self):
        """Toggle the seed entry field based on checkbox state."""
        if self.use_seed.get():
            self.seed_entry.config(state='normal')
        else:
            self.seed_entry.config(state='disabled')
            self.seed_value.set("")
    
    def browse_csv_file(self):
        """Open file dialog to select CSV file."""
        filename = filedialog.askopenfilename(
            title="Select Player Data CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_file_path.set(filename)
            self.preview_csv_data(filename)
            # Auto-set output file path
            if not self.output_file_path.get():
                output_path = os.path.join(os.path.dirname(filename), "groups.html")
                self.output_file_path.set(output_path)
    
    def browse_output_file(self):
        """Open file dialog to select output HTML file."""
        filename = filedialog.asksaveasfilename(
            title="Save HTML Report As",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_path.set(filename)
    
    def preview_csv_data(self, filename):
        """Preview CSV data in the treeview."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Create case-insensitive column mapping
                fieldnames = reader.fieldnames or []
                column_map = {}
                for field in fieldnames:
                    column_map[field.lower()] = field
                
                # Check required columns (case-insensitive)
                required_columns = {'name', 'ranking', 'playing'}
                available_columns = set(column_map.keys())
                
                if not required_columns.issubset(available_columns):
                    missing = required_columns - available_columns
                    self.update_status(f"❌ Missing required columns: {missing}", "error")
                    return
                
                # Check if gender column exists
                has_gender = 'gender' in available_columns
                
                # Load data into treeview
                row_count = 0
                active_count = 0
                for row in reader:
                    # Get column values using case-insensitive mapping
                    name_col = column_map['name']
                    ranking_col = column_map['ranking']
                    playing_col = column_map['playing']
                    gender_col = column_map.get('gender', '') if has_gender else ''
                    
                    name = row[name_col].strip()
                    ranking = row[ranking_col].strip()
                    playing = row[playing_col].strip().lower()
                    gender = row[gender_col].strip() if has_gender and gender_col else ''
                    
                    # Color code based on playing status
                    if playing == 'yes':
                        tags = ('active',)
                        active_count += 1
                    else:
                        tags = ('inactive',)
                    
                    self.tree.insert('', 'end', values=(name, ranking, gender, playing.title()), tags=tags)
                    row_count += 1
                
                # Configure tags for styling
                self.tree.tag_configure('active', background='#e8f5e8')
                self.tree.tag_configure('inactive', background='#f5f5f5', foreground='#666666')
                
                self.update_status(f"✅ Loaded {row_count} players ({active_count} active, {row_count - active_count} inactive)")
                
        except Exception as e:
            self.update_status(f"❌ Error reading CSV file: {str(e)}", "error")
    
    def open_csv_file(self, event):
        """Open the selected CSV file in the default application."""
        if self.csv_file_path.get() and os.path.exists(self.csv_file_path.get()):
            self.open_file(self.csv_file_path.get())
    
    def generate_groups(self):
        """Generate groups using the selected CSV file."""
        if not self.csv_file_path.get():
            messagebox.showerror("Error", "Please select a CSV file first.")
            return
        
        if not self.output_file_path.get():
            messagebox.showerror("Error", "Please specify an output HTML file.")
            return
        
        # Disable the generate button and show progress
        self.generate_button.config(state='disabled')
        self.progress.start()
        self.update_status("🔄 Generating groups...")
        
        # Run generation in a separate thread to prevent UI freezing
        thread = threading.Thread(target=self._generate_groups_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_groups_thread(self):
        """Thread function for group generation."""
        try:
            # Set random seed if specified
            if self.use_seed.get() and self.seed_value.get():
                import random
                seed = int(self.seed_value.get())
                random.seed(seed)
            
            # Create generator and process data
            generator = GroupGenerator(self.csv_file_path.get())
            generator.read_csv()
            generator.create_groups()
            
            # Generate HTML output
            html_gen = HTMLGenerator(generator)
            html_gen.generate_html(self.output_file_path.get())
            
            # Get statistics
            stats = generator.get_statistics()
            
            # Update UI in main thread
            self.root.after(0, self._generation_complete, stats, None)
            
        except Exception as e:
            # Update UI with error in main thread
            self.root.after(0, self._generation_complete, None, str(e))
    
    def _generation_complete(self, stats, error):
        """Handle completion of group generation."""
        # Stop progress and re-enable button
        self.progress.stop()
        self.generate_button.config(state='normal')
        
        if error:
            self.update_status(f"❌ Error: {error}", "error")
            self.update_results("")
        else:
            # Success - update status and results
            self.update_status("✅ Groups generated successfully!")
            
            results = f"""📊 Generation Summary:
• Total players: {stats['total_players']}
• Active players: {stats['active_players']}
• Groups created: {stats['total_groups']}
• Group sizes: {', '.join(map(str, stats['group_sizes']))}
• Ranking distribution:
  - Rank 1: {stats['ranking_counts'][1]} players
  - Rank 2: {stats['ranking_counts'][2]} players  
  - Rank 3: {stats['ranking_counts'][3]} players
  - Rank 4: {stats['ranking_counts'][4]} players

📄 Output saved to: {self.output_file_path.get()}"""
            
            self.update_results(results)
            self.open_html_button.config(state='normal')
    
    def update_status(self, message, status_type="info"):
        """Update the status label."""
        self.status_text.set(message)
        
        # Color code based on status type
        if status_type == "error":
            self.status_label.config(foreground="red")
        elif status_type == "success":
            self.status_label.config(foreground="green")
        else:
            self.status_label.config(foreground="black")
    
    def update_results(self, text):
        """Update the results text area."""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        self.results_text.config(state='disabled')
    
    def open_html_file(self):
        """Open the generated HTML file in the default browser."""
        if self.output_file_path.get() and os.path.exists(self.output_file_path.get()):
            self.open_file(self.output_file_path.get())
    
    def open_file(self, filepath):
        """Open a file using the system's default application."""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', filepath])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(filepath)
            else:  # Linux and others
                subprocess.call(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def on_item_double_click(self, event):
        """Handle double-click on treeview item for editing."""
        if not self.csv_file_path.get():
            return
            
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
            
        # Get the column that was clicked
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        column = self.tree.identify("column", event.x, event.y)
        if not column:
            return
            
        column_index = int(column.replace('#', '')) - 1
        column_names = ['Name', 'Ranking', 'Gender', 'Playing']
        
        if column_index < 0 or column_index >= len(column_names):
            return
            
        # Get current values
        values = list(self.tree.item(item, 'values'))
        current_value = values[column_index]
        
        # Create edit dialog
        self.edit_cell_dialog(item, column_index, column_names[column_index], current_value)
    
    def on_right_click(self, event):
        """Handle right-click context menu."""
        if not self.csv_file_path.get():
            return
            
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Edit Row", command=lambda: self.edit_row_dialog(item))
            context_menu.add_separator()
            context_menu.add_command(label="Delete Row", command=lambda: self.delete_row(item))
            context_menu.add_separator()
            context_menu.add_command(label="Add New Row", command=self.add_new_row)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def edit_cell_dialog(self, item, column_index, column_name, current_value):
        """Show dialog to edit a single cell."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit {column_name}")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text=f"Edit {column_name}:").pack(pady=10)
        
        # Create appropriate input widget based on column
        if column_name == "Ranking":
            var = tk.StringVar(value=current_value)
            entry = ttk.Combobox(dialog, textvariable=var, values=['1', '2', '3', '4'], width=20)
        elif column_name == "Gender":
            var = tk.StringVar(value=current_value)
            entry = ttk.Combobox(dialog, textvariable=var, values=['Male', 'Female'], width=20)
        elif column_name == "Playing":
            var = tk.StringVar(value=current_value)
            entry = ttk.Combobox(dialog, textvariable=var, values=['Yes', 'No'], width=20)
        else:  # Name
            var = tk.StringVar(value=current_value)
            entry = ttk.Entry(dialog, textvariable=var, width=25)
        
        entry.pack(pady=10)
        entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_changes():
            new_value = var.get().strip()
            if new_value:
                # Update treeview
                values = list(self.tree.item(item, 'values'))
                values[column_index] = new_value
                self.tree.item(item, values=values)
                
                # Mark as changed
                self.has_unsaved_changes = True
                self.save_csv_button.config(state='normal')
                self.update_status("📝 Changes made - remember to save!")
                
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to save
        dialog.bind('<Return>', lambda e: save_changes())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def edit_row_dialog(self, item):
        """Show dialog to edit an entire row."""
        values = list(self.tree.item(item, 'values'))
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Player")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=values[0])
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Ranking
        ttk.Label(form_frame, text="Ranking:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ranking_var = tk.StringVar(value=values[1])
        ranking_combo = ttk.Combobox(form_frame, textvariable=ranking_var, values=['1', '2', '3', '4'], width=27)
        ranking_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Gender
        ttk.Label(form_frame, text="Gender:").grid(row=2, column=0, sticky=tk.W, pady=5)
        gender_var = tk.StringVar(value=values[2])
        gender_combo = ttk.Combobox(form_frame, textvariable=gender_var, values=['Male', 'Female'], width=27)
        gender_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Playing
        ttk.Label(form_frame, text="Playing:").grid(row=3, column=0, sticky=tk.W, pady=5)
        playing_var = tk.StringVar(value=values[3])
        playing_combo = ttk.Combobox(form_frame, textvariable=playing_var, values=['Yes', 'No'], width=27)
        playing_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_changes():
            new_values = [
                name_var.get().strip(),
                ranking_var.get().strip(),
                gender_var.get().strip(),
                playing_var.get().strip()
            ]
            
            if all(new_values):
                # Update treeview
                self.tree.item(item, values=new_values)
                
                # Update row styling based on playing status
                if new_values[3].lower() == 'yes':
                    self.tree.item(item, tags=('active',))
                else:
                    self.tree.item(item, tags=('inactive',))
                
                # Mark as changed
                self.has_unsaved_changes = True
                self.save_csv_button.config(state='normal')
                self.update_status("📝 Changes made - remember to save!")
                
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        name_entry.focus()
    
    def delete_row(self, item):
        """Delete a row from the treeview."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this player?"):
            self.tree.delete(item)
            self.has_unsaved_changes = True
            self.save_csv_button.config(state='normal')
            self.update_status("📝 Player deleted - remember to save!")
    
    def add_new_row(self):
        """Add a new row to the treeview."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Player")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Ranking
        ttk.Label(form_frame, text="Ranking:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ranking_var = tk.StringVar(value='1')
        ranking_combo = ttk.Combobox(form_frame, textvariable=ranking_var, values=['1', '2', '3', '4'], width=27)
        ranking_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Gender
        ttk.Label(form_frame, text="Gender:").grid(row=2, column=0, sticky=tk.W, pady=5)
        gender_var = tk.StringVar(value='Male')
        gender_combo = ttk.Combobox(form_frame, textvariable=gender_var, values=['Male', 'Female'], width=27)
        gender_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Playing
        ttk.Label(form_frame, text="Playing:").grid(row=3, column=0, sticky=tk.W, pady=5)
        playing_var = tk.StringVar(value='Yes')
        playing_combo = ttk.Combobox(form_frame, textvariable=playing_var, values=['Yes', 'No'], width=27)
        playing_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def add_player():
            new_values = [
                name_var.get().strip(),
                ranking_var.get().strip(),
                gender_var.get().strip(),
                playing_var.get().strip()
            ]
            
            if all(new_values):
                # Add to treeview
                if new_values[3].lower() == 'yes':
                    tags = ('active',)
                else:
                    tags = ('inactive',)
                
                self.tree.insert('', 'end', values=new_values, tags=tags)
                
                # Mark as changed
                self.has_unsaved_changes = True
                self.save_csv_button.config(state='normal')
                self.update_status("📝 Player added - remember to save!")
                
            dialog.destroy()
        
        ttk.Button(button_frame, text="Add", command=add_player).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        name_entry.focus()
    
    def save_csv_changes(self):
        """Save changes back to the CSV file."""
        if not self.csv_file_path.get() or not self.has_unsaved_changes:
            return
        
        try:
            # Get all data from treeview
            rows = []
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                rows.append({
                    'name': values[0],
                    'ranking': values[1],
                    'gender': values[2],
                    'playing': values[3].lower()
                })
            
            # Write to CSV file
            with open(self.csv_file_path.get(), 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['name', 'ranking', 'gender', 'playing']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            # Reset change tracking
            self.has_unsaved_changes = False
            self.save_csv_button.config(state='disabled')
            self.update_status("✅ Changes saved to CSV file!")
            
            messagebox.showinfo("Success", "Changes have been saved to the CSV file.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
            self.update_status(f"❌ Error saving changes: {str(e)}", "error")


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = ParBuddyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
