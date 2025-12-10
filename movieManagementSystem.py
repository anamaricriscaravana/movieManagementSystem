import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
# from datetime import datetime

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
            'primary_accent': "#3b9ad9"      # Header foreground
        }
    
        # Fonts required for Treeview style
        self.font = font.Font(family='Segoe UI', size=10)
        self.font_bold = font.Font(family='Segoe UI', size=10, weight='bold')
    
        # Configure Styles
        style = ttk.Style()
        style.theme_use('default')

        # Configure Combobox Colors
        self.root.option_add('*TCombobox*Listbox.background', self.colors['input_bg'])
        self.root.option_add('*TCombobox*Listbox.foreground', self.colors['color_fg'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.colors['primary_accent'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.colors['primary_txt'])

        style.map('TCombobox',
            fieldbackground=[('readonly', self.colors['input_bg'])],
            selectbackground=[('readonly', self.colors['input_bg'])],
            selectforeground=[('readonly', self.colors['color_fg'])]
        )
        style.configure('TCombobox',
            background=self.colors['input_bg'],
            foreground=self.colors['color_fg'],
            arrowcolor=self.colors['color_fg'],
            fieldbackground=self.colors['input_bg'],
            bordercolor=self.colors['entry_border']
        )

        # selected movie id
        self.selected_id = None

        # validation setup
        self.year_validation_cmd = self.root.register(self.validate_year_input)
        self.duration_validation_cmd = self.root.register(self.validate_duration_input)

        # initialize database
        self.initialize_database()

        # create GUI
        self.create_widgets()

        # load initial data
        self.refresh_table()

    def get_input_values(self):
        """Returns a dictionary of all movie attributes."""
        return {
        'title': self.title_var.get().strip(),
        'genre': self.genre_var.get().strip(),
        'director': self.director_var.get().strip(),
        'release_year': self.release_year_var.get().strip(),
        'duration': self.duration_var.get().strip(),
        'rating': self.rating_var.get().strip(),
        'language': self.language_var.get().strip(),
        'status': self.status_var.get().strip(),
        'remarks': self.remarks_var.get().strip()
        }

        # validation methods
    def validate_year_input(self, new_text):
        """Allows only 4 digits and checks if the value is purely numeric."""
        if not new_text:
            return True
        if not new_text.isdigit():
            return False
        if len(new_text) > 4:
            return False
        return True    
    
    def validate_duration_input(self, new_text):
        """Allows only positive numeric input for duration."""
        if not new_text:
            return True
        try:
            val = int(new_text)
            return val >= 0
        except ValueError:
            return False

    def create_connection(self):
        """Create database connection""" 
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database:\n{e}")
            return None
        
    def initialize_database(self):
        """Initialize database and create table if not exists""" 
        conn = self.create_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # create movie table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    director TEXT NOT NULL,
                    release_year TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    rating TEXT NOT NULL,
                    language TEXT NOT NULL,
                    status TEXT NOT NULL,
                    remarks TEXT
                )
                """)
            return True
            
            # # check if table has data
            # cursor.execute("SELECT COUNT(*) FROM movies")
            # count = cursor.fetchone()[0] 

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database:\n{e}")
            return False
        finally:
            if conn:
                conn.close()
            # return False

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

        # input variables
        self.title_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.director_var = tk.StringVar()
        self.release_year_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.rating_var = tk.StringVar()
        self.language_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.remarks_var = tk.StringVar()

        # create input fields
        self.create_input_field(input_inner_frame, "Title", self.title_var, 0, 0)
        self.create_input_field(input_inner_frame, "Genre", self.genre_var, 0, 1)
        self.create_input_field(input_inner_frame, "Director", self.director_var, 0, 2)
        
        self.create_input_field(input_inner_frame, "Release Year", self.release_year_var, 1, 0, validate_cmd=self.year_validation_cmd)
        self.create_input_field(input_inner_frame, "Duration (minutes)", self.duration_var, 1, 1, validate_cmd=self.duration_validation_cmd)
        self.create_input_field(input_inner_frame, "Rating", self.rating_var, 1, 2)

        self.create_input_field(input_inner_frame, "Language", self.language_var, 2, 0)
        self.create_input_field(input_inner_frame, "Status", self.status_var, 2, 1, input_type='dropdown', values=['To Watch', 'Watching', 'On Hold', 'Completed'])
        self.create_input_field(input_inner_frame, "Remarks", self.remarks_var, 2, 2)

        # button frame
        button_frame = tk.Frame(self.root, bg=self.colors['primary_bg'], pady=15)
        button_frame.pack(fill="x", padx=20)

        # Create a frame to hold the buttons
        button_inner_frame = tk.Frame(button_frame, bg=self.colors['primary_bg'])
        button_inner_frame.pack(side="top", anchor="center")  # Center the inner frame

        self.create_button(button_inner_frame, "Add Movie", self.colors['add_button'], self.add_movie)
        self.create_button(button_inner_frame, "Update Movie", self.colors['update_button'], self.update_movie)
        self.create_button(button_inner_frame, "Delete Movie", self.colors['delete_button'], self.delete_movie)
        self.create_button(button_inner_frame, "Clear Fields", self.colors['clear_button'], self.clear_fields)

        # table frame
        table_frame = tk.Frame(self.root, bg=self.colors['color_fg'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.create_table(table_frame)

        # Bind selection event
        self.movie_table.bind("<<TreeviewSelect>>", self.on_tree_select)

    # create input field
    def create_input_field(self, parent, label_text, text_variable, row, column, validate_cmd=None, input_type='entry', values=None):
        label = tk.Label(
            parent,
            text=label_text,
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['secondary_bg'],
            fg=self.colors['color_fg'],
            anchor='w'
        )
        label.grid(row=row, column=column, sticky='w', padx=(10,5), pady=5)

        if input_type == 'dropdown':
            combobox = ttk.Combobox(
                parent,
                textvariable=text_variable,
                font=('Segoe UI', 10),
                values=values,
                state='readonly',
                width=26
            )
            combobox.grid(row=row, column=column, padx=(140,5), pady=5, sticky='w')
            if values:
                text_variable.set(values[0])
            return

        entry_options = {
            'textvariable': text_variable,
            'font': ('Segoe UI', 10),
            'width': 28,
            'bg': self.colors['input_bg'],
            'fg': self.colors['color_fg'],
            'relief': 'flat',
            'highlightthickness': 1,
            'highlightbackground': self.colors['entry_border'],
            'insertbackground': self.colors['color_fg']
        }
        
        # Apply validation if command is provided (Fix #5)
        if validate_cmd:
            entry_options['validate'] = 'key'
            # %P means the value of the entry if the edit is allowed
            entry_options['validatecommand'] = (validate_cmd, '%P')

        # Use the options dictionary which includes validation settings
        entry = tk.Entry(parent, **entry_options)
        entry.grid(row=row, column=column, padx=(140,5), pady=5, sticky='w')

    # button
    def create_button(self, parent, text, color, command):
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
            cursor="hand2",
            command=command
        )
        # btn.pack(side="left", padx=10) 
        # btn.pack(side="left", padx=10, pady=5, expand=True)  # Use expand=True to center the buttons
        btn.pack(side="left", padx=10, pady=5) 

    def create_table(self, parent):
        style = ttk.Style()
        
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
        # x_tree_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        # x_tree_scroll.pack(side='bottom', fill='x')

        y_tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        y_tree_scroll.pack(side='right', fill='y')
        
        # Create the Treeview
        self.movie_table = ttk.Treeview(
            tree_frame, 
            yscrollcommand=y_tree_scroll.set, 
            # xscrollcommand=x_tree_scroll.set,
            selectmode="extended"
        )
        self.movie_table.pack(side='left', fill='both', expand=True)
        
        y_tree_scroll.config(command=self.movie_table.yview)
        # x_tree_scroll.config(command=self.movie_table.xview)

        # Define Columns 
        self.movie_table['columns'] = (
            "db_id", "Title", "Genre", "Director", "Year", "Duration", 
            "Rating", "Language", "Status", "Remarks"
        )
        
        # Configure Column Properties
        self.movie_table.column("#0", width=0, stretch='no') # Default hidden column
        self.movie_table.column("db_id", anchor='center', width=0, stretch='no')

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
        self.movie_table.heading("db_id", text="", anchor='center')
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

        # status bar
        status_frame = tk.Frame(self.root, bg=self.colors['tertiary_bg'], height=30)
        status_frame.pack(fill='x', side='bottom')

        self.status_label = tk.Label(
            status_frame,
            text=f"Ready | Database:{DB_FILE}",
            font=('Segoe UI', 10),
            bg=self.colors['tertiary_bg'],
            fg=self.colors['color_fg'],
            anchor='w'
        )
        self.status_label.pack(fill='x', padx=10, pady=8)

    def clear_fields(self):
        """Clear all input fields"""
        self.title_var.set("")
        self.genre_var.set("")
        self.director_var.set("")
        self.release_year_var.set("")
        self.duration_var.set("")
        self.rating_var.set("")
        self.language_var.set("")
        self.status_var.set("")
        self.remarks_var.set("")
        self.selected_id = None
        self.status_label.config(text="Cleared all input fields.")
    
        # Clear selection in tree
        for item in self.movie_table.selection():
            self.movie_table.selection_remove(item)

    def refresh_table(self):
        """Refresh the student table""" 
        conn = self.create_connection()
        if not conn:
            return
        
        try:
            # clear existing data
            for item in self.movie_table.get_children():
                self.movie_table.delete(item) 

            # Fetch all movies
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movies ORDER BY title ASC")
            rows = cursor.fetchall()

            # insert data into treeview
            for row in rows:
                self.movie_table.insert(
                '', 
                'end', 
                values=(
                    row['id'],
                    row['title'], row['genre'], row['director'], row['release_year'],
                    row['duration'], row['rating'], row['language'], row['status'], row['remarks']
                )
            )

            # update status
            count = len(rows)
            self.status_label.config(text=f"Loaded {count} movies from database {DB_FILE}.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load movies:\n{e}")
        finally:
            conn.close()

    def on_tree_select(self, event):
        """Handle tree selection event""" 
        selection = self.movie_table.selection()
        if not selection:
            self.clear_fields()
            return
        
        # Get selected item
        item = selection[0]
        values = self.movie_table.item(item, 'values')

        # Load data into fields
        self.selected_id = values[0]
        self.title_var.set(values[1])
        self.genre_var.set(values[2])
        self.director_var.set(values[3])
        self.release_year_var.set(values[4])
        self.duration_var.set(values[5])
        self.rating_var.set(values[6])
        self.language_var.set(values[7])
        self.status_var.set(values[8])
        self.remarks_var.set(values[9])
        self.status_label.config(text=f"Selected Movie Title: {self.title_var.get()}")

    def add_movie(self):
        """Add new movie to database""" 
        # Get and validate input
        data = self.get_input_values()

        # Validation
        if not all([data['title'], data['genre'], data['director'], data['release_year'], data['duration'], data['rating'], data['language'], data['status']]):
            messagebox.showwarning("Validation Error", "All fields are required!")
            return

        # validate release year
        if not data['release_year'].isdigit() or len(data['release_year']) !=4:
            messagebox.showwarning("Validation Error", "Release Year must be a valid 4-digit year!")
            return

        # Validation for duration (numeric check)
        try:
            duration = int(data['duration'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Duration must be an integer (minutes).")
            return
        
        conn = self.create_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            # Insert data into the movies table
            cursor.execute(
                """
                INSERT INTO movies (title, genre, director, release_year, duration, rating, language, status, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (data['title'], data['genre'], data['director'], data['release_year'], duration, data['rating'], data['language'], data['status'], data['remarks'])
            )
        
            conn.commit()
            messagebox.showinfo("Success", f"Movie '{data['title']}' added successfully!")
            self.clear_fields()
            self.refresh_table()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add movie:\n{e}")
        finally:
            conn.close()

    def update_movie(self):
        """Update selected movie""" 
        if not self.selected_id:
            messagebox.showwarning(
            "Selection Required",
            "Please select a movie record first by clicking on it in the table."
            )
            return

        # get validate input
        data = self.get_input_values()

        # Validation
        if not all([data['title'], data['genre'], data['director'], data['release_year'], data['duration'], data['rating'], data['language'], data['status']]):
            messagebox.showwarning("Validation Error", "All fields are required!")
            return      
    
            # validate release year
        if not data['release_year'].isdigit() or len(data['release_year']) != 4:
            messagebox.showwarning("Validation Error", "Release Year must be a valid 4-digit year!")
            return

        # Validation for duration (numeric check)
        try:
            duration = int(data['duration'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Duration must be an integer (minutes).")
            return
        
        conn = self.create_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            # update data into the movies table
            cursor.execute(
                """
                UPDATE movies SET title=?, genre=?, director=?, release_year=?, duration=?, rating=?, language=?, status=?, remarks=?
                WHERE id=?
                """,
                (data['title'], data['genre'], data['director'], data['release_year'], duration, data['rating'], data['language'], data['status'], data['remarks'], self.selected_id)
            )
        
            conn.commit()
            messagebox.showinfo("Success", f"Movie '{data['title']}' updated successfully!")

            self.clear_fields()
            self.refresh_table()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add movie:\n{e}")
        finally:
            conn.close()

    def delete_movie(self):
        """Delete selected movie""" 
        if not self.selected_id:
            messagebox.showwarning(
            "Selection Required",
            "Please select a movie record first by clicking on it in the table."
            )
            return
    
        # Confirm deletion
        response = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this movie record?\nThis action cannot be undone."
        )

        if not response:
            return

        # Delete from database
        conn = self.create_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movies WHERE id=?", (self.selected_id,))
            conn.commit()

            messagebox.showinfo("Success", f"Movie ID {self.selected_id} deleted successfully.")
            self.clear_fields()
            self.refresh_table()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete movie:\n{e}")
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    window = tk.Tk()
    app = MovieManagementSystem(window)
    window.mainloop()