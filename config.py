from tkinter import ttk

# window settings
WINDOW_TITLE = "Movie Management System"
WINDOW_SIZE = "1100x700"

STATUS_OPTIONS = ['To Watch', 'Watching', 'On Hold', 'Completed']
TABLE_COLUMNS = ("id", "Title", "Genre", "Director", "Year", "Duration", "Rating", "Language", "Status", "Remarks")

# Column widths for Treeview
COLUMN_WIDTHS = {
    "id": 0,
    "Title": 150,
    "Genre": 100,
    "Director": 120,
    "Year": 60,
    "Duration": 80,
    "Rating": 60,
    "Language": 100,
    "Status": 100,
    "Remarks": 250
}

# Color palette for UI styling
COLORS = {
    'primary_bg': '#1b1f3b', 
    'secondary_bg': '#2e3355', 
    'input_bg': '#3b4169',
    'color_fg': 'white', 
    'entry_border': "#515b93", 
    'add_button': "#93C9AB",
    'update_button': "#FFE28B", 
    'delete_button': "#FC7F71", 
    'clear_button': "#E1F0FA",
    'primary_txt': '#ffffff', 
    'tertiary_bg': '#14172a', 
    'primary_accent': "#3b9ad9"
}

# Apply ttk styles to Treeview and Combobox
def apply_styles(root, font, font_bold):
    style = ttk.Style()
    style.theme_use('default')

    # Treeview configuration
    style.configure("Treeview", 
                    background=COLORS['secondary_bg'], 
                    foreground='white', 
                    fieldbackground=COLORS['secondary_bg'], 
                    font=font, 
                    rowheight=25)
    style.map('Treeview', 
              background=[('selected', COLORS['primary_accent'])])
    
    # Treeview heading
    style.configure("Treeview.Heading", 
                    background=COLORS['tertiary_bg'], 
                    foreground='white', 
                    font=font_bold, 
                    relief="flat")
    
    # Combobox styling
    style.map('TCombobox', 
              fieldbackground=[('readonly', COLORS['input_bg'])], 
              selectbackground=[('readonly', COLORS['input_bg'])])
    style.configure('TCombobox', 
                    background=COLORS['input_bg'], 
                    foreground='white')
    root.option_add('*TCombobox*Listbox.background', COLORS['input_bg'])
    root.option_add('*TCombobox*Listbox.foreground', 'white')

# API Keys
TMDB_API_KEY = "d758564ccd7127ab4e0e38901e85d76a"
OMDB_API_KEY = "d8257053" 