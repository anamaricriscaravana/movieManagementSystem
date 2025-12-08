import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from datetime import datetime

DB_FILE = "movie_management.db"

class MovieManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Management System")
        self.root.geometry("1100x700")
        self.root.configure(bg="#1b1f3b")   # for the theme background
        self.root.resizable(True, True)

        # color scheme
        self.colors = {
            'primary_bg': '#1b1f3b',
            # 'primary_bg': '#052e56',
            'secondary_bg': '#2e3355',
            'input_bg': '#3b4169',
            'color_fg': 'white',
            'entry_border': "#515b93",
            # 'add_button': "#2ecc71",
            'add_button': "#93C9AB",
            # 'update_button': "#f1c40f",
            'update_button': "#FFE28B",
            # 'delete_button': "#e74c3c",
            'delete_button': "#FC7F71",
            # 'clear_button': "#3498db",
            'clear_button': "#E1F0FA",
            'primary_txt': '#ffffff',      # Text color for table rows
            'tertiary_bg': '#14172a',      # Header background
            'primary_accent': "#3b9ad9c7",    # Header foreground
        }
    
        # Fonts required for Treeview style
        self.font = font.Font(family='Segoe UI', size=10)
        self.font_bold = font.Font(family='Segoe UI', size=10, weight='bold')
    
        self.create_widgets()

    def create_widgets(self):

        # header frame
        header_frame = tk.Frame(self.root, bg=self.colors['primary_bg'], height=60)
        header_frame.pack(fill="x")
        header_label = tk.Label(
            header_frame,
            text="MOVIE MANAGEMENT SYSTEM",
            font=('Segoe UI', 22, 'bold'),
            bg=self.colors['primary_bg'],
            fg="white",
            pady=20
        )
        header_label.pack()

        # input frame
        input_frame = tk.Frame(self.root, bg=self.colors['secondary_bg'], pady=20)
        input_frame.pack(fill="x", padx=20, pady=10)

        # Create a frame to hold the buttons
        input_inner_frame = tk.Frame(input_frame, bg=self.colors['secondary_bg'])
        input_inner_frame.pack(side="top", anchor="center")  # Center the inner frame

        self.title_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.director_var = tk.StringVar()
        self.release_year_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.rating_var = tk.StringVar()
        self.language_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.remarks_var = tk.StringVar()

        # fields
        self.create_input_field(input_inner_frame, "Title", self.title_var, 0, 0)
        self.create_input_field(input_inner_frame, "Genre", self.genre_var, 0, 1)
        self.create_input_field(input_inner_frame, "Director", self.director_var, 0, 2)
        
        self.create_input_field(input_inner_frame, "Release Year", self.release_year_var, 1, 0)
        self.create_input_field(input_inner_frame, "Duration (minutes)", self.duration_var, 1, 1)
        self.create_input_field(input_inner_frame, "Rating", self.rating_var, 1, 2)

        self.create_input_field(input_inner_frame, "Language", self.language_var, 2, 0)
        self.create_input_field(input_inner_frame, "Status", self.status_var, 2, 1)
        self.create_input_field(input_inner_frame, "Remarks", self.remarks_var, 2, 2)

        # button frame
        button_frame = tk.Frame(self.root, bg=self.colors['primary_bg'], pady=15)
        button_frame.pack(fill="x", padx=20)

        # Create a frame to hold the buttons
        button_inner_frame = tk.Frame(button_frame, bg=self.colors['primary_bg'])
        button_inner_frame.pack(side="top", anchor="center")  # Center the inner frame

        self.create_button(button_inner_frame, "Add Movie", self.colors['add_button'])
        self.create_button(button_inner_frame, "Update Movie", self.colors['update_button'])
        self.create_button(button_inner_frame, "Delete Movie", self.colors['delete_button'])
        self.create_button(button_inner_frame, "Clear Fields", self.colors['clear_button'])

        # table frame
        table_frame = tk.Frame(self.root, bg=self.colors['color_fg'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.create_table(table_frame)

    # create input field
    def create_input_field(self, parent, label_text, text_variable, row, column):
        label = tk.Label(
            parent,
            text=label_text,
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['secondary_bg'],
            fg=self.colors['color_fg'],
            anchor='w'
        )
        label.grid(row=row, column=column, sticky='w', padx=(10,5), pady=5)

        entry = tk.Entry(
            parent,
            textvariable=text_variable,
            font=('Segoe UI', 10),
            width=28,
            bg=self.colors['input_bg'],
            fg=self.colors['color_fg'],
            relief='flat',
            highlightthickness=1, #border thickness
            highlightbackground=self.colors['entry_border'] #border color
        )
        entry.grid(row=row, column=column, padx=(140,5), pady=5, sticky='w')

    # button
    def create_button(self, parent, text, color):
        btn = tk.Button(
            parent,
            text=text,
            bg=color,
            fg="black",
            font=('Segoe UI', 11, 'bold'),
            width=15,
            activebackground=color,
            relief='flat',
            bd=0,
            cursor="hand2"
        )
        # btn.pack(side="left", padx=10) 
        # btn.pack(side="left", padx=10, pady=5, expand=True)  # Use expand=True to center the buttons
        btn.pack(side="left", padx=10, pady=5) 

    def create_table(self, parent):
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure the Treeview itself (rows)
        style.configure(
            "Treeview", 
            background=self.colors['secondary_bg'],
            foreground=self.colors['primary_txt'],
            fieldbackground=self.colors['secondary_bg'],
            font=self.font,
            rowheight=25,
            bordercolor=self.colors['primary_bg']
        )
        style.map('Treeview', background=[('selected', self.colors['primary_accent'])])
        
        # Configure the Treeview Headings
        style.configure(
            "Treeview.Heading", 
            background=self.colors['tertiary_bg'],
            foreground=self.colors['primary_txt'],
            font=self.font_bold,
            padding=5,
            relief="flat"
        )
        
        style.map(
            "Treeview.Heading",
            background=[('active', self.colors['secondary_bg'])]
        )

        tree_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        tree_frame.pack(fill='both', expand=True)

        # Scrollbars
        x_tree_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_tree_scroll.pack(side='bottom', fill='x')

        y_tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        y_tree_scroll.pack(side='right', fill='y')
        
        # Create the Treeview
        self.movie_table = ttk.Treeview(
            tree_frame, 
            yscrollcommand=y_tree_scroll.set, 
            xscrollcommand=x_tree_scroll.set,
            selectmode="extended"
        )
        self.movie_table.pack(side='left', fill='both', expand=True)
        
        y_tree_scroll.config(command=self.movie_table.yview)
        x_tree_scroll.config(command=self.movie_table.xview)

        # Define Columns 
        self.movie_table['columns'] = (
            "Title", "Genre", "Director", "Year", "Duration", 
            "Rating", "Language", "Status", "Remarks"
        )
        
        # Configure Column Properties
        self.movie_table.column("#0", width=0, stretch='no') # Default hidden column
        # self.movie_table.column("ID", anchor='center', width=50, stretch='no')
        self.movie_table.column("Title", anchor='w', width=200)
        self.movie_table.column("Genre", anchor='w', width=120)
        self.movie_table.column("Director", anchor='w', width=140)
        self.movie_table.column("Year", anchor='center', width=60)
        self.movie_table.column("Duration", anchor='center', width=110)
        self.movie_table.column("Rating", anchor='center', width=60)
        self.movie_table.column("Language", anchor='w', width=120)
        self.movie_table.column("Status", anchor='w', width=100)
        self.movie_table.column("Remarks", anchor='w', width=300)

        # Configure Headings
        self.movie_table.heading("#0", text="", anchor='w')
        # self.movie_table.heading("ID", text="ID", anchor='center')
        self.movie_table.heading("Title", text="Title", anchor='w')
        self.movie_table.heading("Genre", text="Genre", anchor='w')
        self.movie_table.heading("Director", text="Director", anchor='w')
        self.movie_table.heading("Year", text="Year", anchor='center')
        self.movie_table.heading("Duration", text="Duration (min)", anchor='center')
        self.movie_table.heading("Rating", text="Rating", anchor='center')
        self.movie_table.heading("Language", text="Language", anchor='w')
        self.movie_table.heading("Status", text="Status", anchor='w')
        self.movie_table.heading("Remarks", text="Remarks", anchor='w')

        # for col in self.movie_table['columns']:
        #     self.movie_table.column(col, anchor='w', width=120)
        #     self.movie_table.heading(col, text=col, anchor='w')

if __name__ == "__main__":
    window = tk.Tk()
    app = MovieManagementSystem(window)
    window.mainloop()