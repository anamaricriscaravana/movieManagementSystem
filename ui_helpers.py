import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageOps, ImageDraw

import config
import api_handler
import database

def center_window(root, width=1100, height=700):
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

def update_clock(label, root):
    if not label.winfo_exists(): return
    label.config(text=time.strftime('%H:%M:%S\n%B %d, %Y'))
    root.after(1000, lambda: update_clock(label, root))

def validate_year_input(P):
    return (P.isdigit() and len(P) <= 4) or P == ""

def create_input_box(parent, title, font_bold, colors):
    box = tk.LabelFrame(parent, text=f" {title} ", font=font_bold, 
                        bg=colors['secondary_bg'], fg="white", padx=20, pady=15)
    
    box.grid_columnconfigure(0, weight=1)  
    box.grid_columnconfigure(1, weight=0)  
    box.grid_columnconfigure(2, weight=0)  
    box.grid_columnconfigure(3, weight=1)  
    return box

def create_input_field(parent, label, var, row, font_bold, font_std, colors, 
                       is_api=False, input_type='entry', values=None, validate_cmd=None, **kwargs):
    
    tk.Label(parent, text=label, font=font_bold, bg=colors['secondary_bg'], 
             fg="white", anchor='w').grid(row=row, column=1, sticky='e', padx=10, pady=5)
    
    if input_type == 'dropdown':
        ent = ttk.Combobox(parent, textvariable=var, values=values, state='readonly', width=35)
    else:
        mask = kwargs.pop('show', None) 
        if kwargs.pop('is_password', False):
            mask = "*"

        ent = tk.Entry(parent, textvariable=var, font=font_std, width=32, 
                       bg=colors['input_bg'], fg="white", relief='flat', 
                       insertbackground='white', show=mask)
        
        if is_api: 
            ent.config(state='readonly', readonlybackground=colors['secondary_bg'])
        if validate_cmd: 
            ent.config(validate='key', validatecommand=(validate_cmd, '%P'))
            
    ent.grid(row=row, column=2, padx=10, pady=5, sticky='w')
    return ent

def create_action_button(parent, text, color, font, command):
    return tk.Button(
        parent, text=text, bg=color, font=font, width=15,
        relief='flat', cursor="hand2", command=command
    )

def create_search_bar(parent, colors, font, on_key_release):
    sb_frame = tk.Frame(parent, bg=colors['input_bg'], 
                        highlightbackground=colors['entry_border'], 
                        highlightthickness=1)
    
    entry = tk.Entry(sb_frame, font=font, bg=colors['input_bg'], 
                     fg="white", borderwidth=0, width=30, insertbackground='white')
    entry.pack(side="left", padx=10, pady=5)
    entry.insert(0, "Search")
    
    entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == "Search" else None)
    entry.bind("<FocusOut>", lambda e: entry.insert(0, "Search") if entry.get() == "" else None)
    entry.bind("<KeyRelease>", on_key_release)
    
    return sb_frame, entry

def create_profile_menu(root, colors, font, commands):
    menu = tk.Menu(root, tearoff=0, bg=colors['secondary_bg'], fg="white", font=font)
    menu.add_command(label="My Profile & Stats", command=commands.get('profile'))
    menu.add_command(label="System Settings", command=commands.get('settings'))
    menu.add_separator()
    menu.add_command(label="Logout", command=commands.get('logout'))
    return menu

def process_profile_image(image_path, size=(150, 150)):
    if not image_path or not os.path.exists(image_path): return None
    try:
        final_size = (160, 160)
        img = Image.open(image_path).convert("RGBA")
        
        output = ImageOps.fit(img, size, centering=(0.5, 0.5))
        
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output.putalpha(mask)

        canvas_img = Image.new("RGBA", final_size, (0, 0, 0, 0))
        idraw = ImageDraw.Draw(canvas_img)
        idraw.ellipse((2, 2, 158, 158), outline="white", width=4)
        canvas_img.paste(output, (5, 5), output)
        
        return ImageTk.PhotoImage(canvas_img)
    except:
        return None

def setup_movie_table(parent):
    y_s = ttk.Scrollbar(parent, orient="vertical")
    y_s.pack(side='right', fill='y')
    x_s = ttk.Scrollbar(parent, orient="horizontal")
    x_s.pack(side='bottom', fill='x')
    
    table = ttk.Treeview(parent, columns=config.TABLE_COLUMNS, 
                         show="headings", yscrollcommand=y_s.set, xscrollcommand=x_s.set)
    
    for col in config.TABLE_COLUMNS:
        width = config.COLUMN_WIDTHS.get(col, 100)
        table.heading(col, text=col, anchor='w')
        table.column(col, anchor='w', width=width, minwidth=width)
    
    table.column("id", width=0, stretch=False)
    table.pack(side='left', fill='both', expand=True)
    
    y_s.config(command=table.yview)
    x_s.config(command=table.xview)
    return table

def add_movie_logic(user_id, title, year, status, remarks, refresh_callback, clear_callback):
    if not title or not year: 
        return messagebox.showwarning("Warning", "Title and Year required!")
    
    data = api_handler.fetch_movie_metadata(title, year)
    if data:
        omdb = data['omdb']
        database.add_movie_to_db(user_id, title, omdb.get('Genre'), omdb.get('Director'), year, 
                                 omdb.get('Runtime'), omdb.get('imdbRating'), 
                                 omdb.get('Language'), status, remarks)
        messagebox.showinfo(f"Success", f"'{title}' added successfully!")
        refresh_callback()
        clear_callback()
    
def update_movie_logic(selected_id, title, year, status, remarks, refresh_callback):
    if not selected_id: 
        return messagebox.showwarning("Error", "Select a record first.")
    
    data = api_handler.fetch_movie_metadata(title, year)
    if data:
        omdb = data['omdb']
        database.update_movie_in_db(
            selected_id, title, omdb.get('Genre'), omdb.get('Director'), 
            year, omdb.get('Runtime'), omdb.get('imdbRating'), 
            omdb.get('Language'), status, remarks
        )
        messagebox.showinfo("Success", f"Movie '{title}' updated successfully!")
        refresh_callback()
    else:
        messagebox.showerror("Error", "API Error. Could not fetch metadata.")

def delete_movie_logic(selected_id, refresh_callback, clear_callback):
    if not selected_id: return
    
    if messagebox.askyesno("Confirm", "Delete this movie record?"):
        database.delete_movie_from_db(selected_id)
        messagebox.showinfo("Success", "Record deleted.")
        refresh_callback()
        clear_callback()