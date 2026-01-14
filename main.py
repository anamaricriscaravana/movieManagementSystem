import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from PIL import Image, ImageTk
import webbrowser, threading, os, shutil
from collections import Counter
import sqlite3

# import modules
import config          
import api_handler      
import ui_helpers       
import authentication   
import database         
import file_handler
import profile_view
import recommendations_view

class MovieManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.minsize(1000, 700)
        self.root.configure(bg=config.COLORS['primary_bg'])
        self.database_module = database
        
        database.initialize_database()
        self.colors = config.COLORS
        self.font = font.Font(family='Segoe UI', size=10)
        self.font_bold = font.Font(family='Segoe UI', size=10, weight='bold')

        self._setup_variables()
        self.container = tk.Frame(self.root, bg=self.colors['primary_bg'])
        self.container.pack(fill="both", expand=True)

        ui_helpers.center_window(self.root)
        self.show_login_page()

    def _setup_variables(self):
        self.current_user_id, self.current_username, self.selected_id = None, None, None
        self.username_var, self.password_var, self.confirm_password_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.title_var, self.genre_var, self.director_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.release_year_var, self.duration_var, self.rating_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.language_var, self.status_var, self.remarks_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.raw_poster_image, self.current_poster, self.current_trailer_url = None, None, None

    def deselect_table(self, event):
        widget = event.widget
        if "treeview" not in str(widget).lower() and "entry" not in str(widget).lower() and "combobox" not in str(widget).lower():
            self.clear_fields()

    def _clear_view(self):
        for widget in self.container.winfo_children(): widget.destroy()

    def get_profile_image(self, size=(150, 150)):
        path = database.get_user_profile_path(self.current_user_id)
        if path:
            return ui_helpers.process_profile_image(path, size)
        return None

    def change_profile_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            if not os.path.exists("uploads"): os.makedirs("uploads")
            dest = os.path.join("uploads", f"profile_{self.current_user_id}{os.path.splitext(file_path)[1]}")
            shutil.copy(file_path, dest)
            conn = database.create_connection(); conn.execute("UPDATE users SET profile_path = ? WHERE id = ?", (dest, self.current_user_id)); conn.commit(); conn.close()
            self.show_profile_view()

    def remove_profile_photo(self):
        try:
            current_path = database.get_user_profile_path(self.current_user_id)
            if not current_path or current_path == "":
                return messagebox.showwarning("Profile Update", 
                    "You are already using the default profile icon. There is no photo to remove.")
            confirm = messagebox.askyesno("Confirm Removal", 
                "Are you sure you want to remove your profile photo and use the default icon?")
            
            if confirm:
                database.clear_user_profile_path(self.current_user_id)
                messagebox.showinfo("Success", "Profile photo removed.")
                self.show_profile_view()
        except Exception as e:
            messagebox.showerror("Error", f"Could not verify profile status: {str(e)}")

    def show_login_page(self):
        self._clear_view(); self.clear_auth_fields()
        self.root.bind('<Return>', lambda e: self.attempt_login())
        authentication.Authentication(self.container, self).render_login()

    def show_register_page(self):
        self._clear_view()
        self.clear_auth_fields() 
        self.root.bind('<Return>', lambda e: self.attempt_register())
        authentication.Authentication(self.container, self).render_register()

    def show_main_app(self):
        self._clear_view(); self.root.unbind('<Return>')
        config.apply_styles(self.root, self.font, self.font_bold)
        
        self.header = self._build_header()
        self.input_section = self._build_input_section()
        self.action_bar = self._build_action_bar()
        self.content_area = self._build_content_area()

        for w in [self.container, self.header, self.input_section, self.action_bar, self.content_area]:
            w.bind("<Button-1>", self.deselect_table)
        self.refresh_table()

    def show_profile_view(self):
        profile_view.ProfileView(self.container, self).render()

    def open_change_username(self):
        authentication.Authentication(self.container, self).open_change_username_popup()

    def open_change_password(self):
        authentication.Authentication(self.container, self).open_change_password_popup()

    def _secure_save_username(self, current_pass, new_username, confirm_pass, win):
        trimmed_u = new_username.strip()

        if trimmed_u == self.current_username:
            return messagebox.showwarning("Security", f"You are already using '{trimmed_u}'. Choose a different one.")
        if not current_pass or not trimmed_u or not confirm_pass:
            return messagebox.showwarning("Warning", "All fields are required.")
        if len(trimmed_u) < 5 or len(trimmed_u) > 15:
            return messagebox.showwarning("Security", "Username must be 5-15 characters.")
        if current_pass != confirm_pass:
            return messagebox.showerror("Error", "Confirmation password mismatch.")
        if not messagebox.askyesno("Confirm", f"Change username to '{trimmed_u}' and logout?"):
            return

        success, message = database.update_username_secure(self.current_user_id, current_pass, trimmed_u)

        if success:
            win.grab_release() 
            win.destroy()
            messagebox.showinfo("Success", "Username changed! Please log in again.")
            self.show_login_page()
        else:
            messagebox.showerror("Error", message)
    
    def _handle_password_update(self, current_pass, new_pass, confirm_pass, win):
        if not current_pass or not new_pass or not confirm_pass:
            return messagebox.showwarning("Warning", "All fields are required.")
        if new_pass == current_pass:
            return messagebox.showwarning("Security Error", "New password cannot be the same as current.")
        if len(new_pass) < 8:
            return messagebox.showwarning("Security", "Password must be at least 8 characters.")
        if new_pass != confirm_pass:
            return messagebox.showerror("Mismatch", "New passwords do not match.")
        if not messagebox.askyesno("Confirm", "Update password and logout?"):
            return 

        success, message = database.update_password_secure(self.current_user_id, current_pass, new_pass)

        if success:
            win.destroy()
            messagebox.showinfo("Success", "Password updated successfully!")
            self.show_login_page()
        else:
            messagebox.showerror("Error", message)
                        
    def show_settings_page(self):
        self._clear_view()
        authentication.Authentication(self.container, self).render_settings()

    def export_as_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")]
        )
        if path:
            try:
                movies = database.get_movies_for_export(self.current_user_id)
                file_handler.save_to_csv(path, movies)
                
                messagebox.showinfo("Success", f"CSV file saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    def export_as_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")]
        )
        if path:
            try:
                movies = database.get_movies_for_export(self.current_user_id)
                file_handler.save_to_pdf(path, movies)
                messagebox.showinfo("Success", f"PDF report saved to:\n{path}")
            except ImportError:
                messagebox.showerror("Error", "Please install reportlab: pip install reportlab")
            except Exception as e:
                messagebox.showerror("Error", f"PDF Export failed: {str(e)}")

    def _build_header(self):
        header = tk.Frame(self.container, bg=self.colors['primary_bg']); header.pack(fill="x", padx=25, pady=10)
        tk.Label(header, text="🎬CINETRACK", font=('Segoe UI', 24, 'bold'), bg=self.colors['primary_bg'], fg="white").pack(side="left")
        profile_btn = tk.Button(header, text=f"{self.current_username} 👤 ▼", font=('Segoe UI', 10, 'bold'), bg=self.colors['secondary_bg'], fg="white", relief="flat", padx=10, cursor="hand2"); profile_btn.pack(side="right"); profile_btn.bind("<Button-1>", self.show_profile_menu)
        return header

    def _build_input_section(self):
        main_f = tk.Frame(self.container, bg=self.colors['primary_bg'])
        main_f.pack(fill="x", padx=25, pady=5)
        
        box1 = ui_helpers.create_input_box(main_f, " Movie Details ", self.font_bold, self.colors)
        box1.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        manual_fields = [
            ("Title:", self.title_var, 0, None),
            ("Year:", self.release_year_var, 1, self.root.register(ui_helpers.validate_year_input)),
            ("Status:", self.status_var, 2, 'dropdown'),
            ("Remarks:", self.remarks_var, 3, None)
        ]
        
        for label, var, row, extra in manual_fields:
            if extra == 'dropdown':
                ui_helpers.create_input_field(box1, label, var, row, self.font_bold, self.font, self.colors, 
                                            input_type='dropdown', values=config.STATUS_OPTIONS)
            else:
                ui_helpers.create_input_field(box1, label, var, row, self.font_bold, self.font, self.colors, 
                                            validate_cmd=extra)

        box2 = ui_helpers.create_input_box(main_f, " Movie Data ", self.font_bold, self.colors)
        box2.pack(side="left", fill="both", expand=True)
        
        api_fields = [
            ("Genre", self.genre_var, 0),
            ("Director", self.director_var, 1),
            ("Duration", self.duration_var, 2),
            ("Language", self.language_var, 3),
            ("Rating", self.rating_var, 4)
        ]
        for label, var, row in api_fields:
            ui_helpers.create_input_field(box2, label, var, row, self.font_bold, self.font, self.colors, is_api=True)
        return main_f

    def _build_action_bar(self):
        frame = tk.Frame(self.container, bg=self.colors['primary_bg'], pady=15)
        frame.pack(fill="x", padx=25)
        
        buttons_config = [
            ("Add Movie", self.colors['add_button'], self.add_movie),
            ("Update", self.colors['update_button'], self.update_movie),
            ("Delete", self.colors['delete_button'], self.delete_movie),
            ("Clear", self.colors['clear_button'], self.clear_fields),
            ("More Like This",self.colors['primary_accent'], self.show_similar_movies_popup)
        ]

        for text, color, cmd in buttons_config:
            btn = ui_helpers.create_action_button(frame, text, color, self.font_bold, cmd)
            btn.pack(side="left", padx=10, pady=5)

        sb_container, self.search_entry = ui_helpers.create_search_bar(
            frame, self.colors, ('Segoe UI', 11), self.filter_table
        )
        sb_container.pack(side="right")
        return frame

    def _build_content_area(self):
        main_c = tk.Frame(self.container, bg=self.colors['primary_bg']); main_c.pack(fill="both", expand=True, padx=25, pady=(0,15))
        self.preview = tk.Frame(main_c, bg=self.colors['secondary_bg'], width=300); self.preview.pack(side="left", fill="both", padx=(0, 15)); self.preview.pack_propagate(False); self.preview.bind("<Configure>", self.on_preview_resize)
        tk.Label(self.preview, text="Preview", font=('Segoe UI', 12, 'bold'), bg=self.colors['secondary_bg'], fg="white").pack(pady=10)
        self.poster_lab = tk.Label(self.preview, text="No Poster Loaded", bg=self.colors['secondary_bg'], fg="white"); self.poster_lab.pack(fill="both", expand=True, padx=15)
        self.watch_btn = tk.Button(self.preview, text="▶ WATCH TRAILER", font=self.font_bold, fg="black", bg="gray", relief='flat', state="disabled", command=self.open_trailer); self.watch_btn.pack(side="bottom", pady=20)
        table_f = tk.Frame(main_c, bg=self.colors['secondary_bg']); table_f.pack(side="right", fill="both", expand=True)
        self.movie_table = ui_helpers.setup_movie_table(table_f); self.movie_table.bind("<<TreeviewSelect>>", self.on_tree_select)
        return main_c

    def add_movie(self): ui_helpers.add_movie_logic(self.current_user_id, self.title_var.get(), self.release_year_var.get(), self.status_var.get(), self.remarks_var.get(), self.refresh_table, self.clear_fields)
    def update_movie(self): ui_helpers.update_movie_logic(self.selected_id, self.title_var.get(), self.release_year_var.get(), self.status_var.get(), self.remarks_var.get(), self.refresh_table)
    def delete_movie(self): ui_helpers.delete_movie_logic(self.selected_id, self.refresh_table, self.clear_fields)

    def refresh_table(self):
        for i in self.movie_table.get_children(): 
            self.movie_table.delete(i)
        rows = database.get_user_movies(self.current_user_id)
        for r in rows: 
            self.movie_table.insert('', 'end', values=tuple(r))

    def filter_table(self, event=None):
        val = self.search_entry.get().strip().lower()
        if val == "search" or val == "":
            self.refresh_table()
            return
        for i in self.movie_table.get_children():
            self.movie_table.delete(i)
        rows = database.search_movies(self.current_user_id, val)
        for r in rows:
            self.movie_table.insert('', 'end', values=tuple(r))

    def clear_fields(self):
        for v in [self.title_var, self.genre_var, self.director_var, self.release_year_var, self.duration_var, self.rating_var, self.language_var, self.status_var, self.remarks_var]: 
            v.set("")
        self.raw_poster_image = None
        self.poster_lab.config(image="", text="No Poster Loaded")
        self.watch_btn.config(state="disabled", bg="gray")
        self.selected_id = None
        if hasattr(self, 'movie_table'):
            self.movie_table.selection_remove(self.movie_table.selection())

    def on_tree_select(self, event):
        sel = self.movie_table.selection()
        if not sel: return
        item = self.movie_table.item(sel[0], 'values'); self.selected_id = item[0]
        self.title_var.set(item[1]); self.release_year_var.set(item[4]); self.status_var.set(item[8]); self.remarks_var.set(item[9])
        self.poster_lab.config(image="", text="Loading Poster..."); self.watch_btn.config(state="disabled", bg="gray")
        api_handler.load_movie_details(item[1], item[4], {'genre': self.genre_var, 'director': self.director_var, 'duration': self.duration_var, 'rating': self.rating_var, 'language': self.language_var}, {'on_trailer_load': self._update_trailer_state, 'on_poster_load': self._update_poster_state})

    def _update_trailer_state(self, url):
        self.root.after(0, lambda: self._safe_update_trailer(url))

    def _safe_update_trailer(self, url):
        self.current_trailer_url = url
        if self.watch_btn.winfo_exists():
            self.watch_btn.config(state="normal" if url else "disabled", bg=self.colors['delete_button'] if url else "gray")

    def _update_poster_state(self, poster):
        if poster:
            self.raw_poster_image = poster
            self.root.after(0, self.update_poster_size)
        else:
            self.raw_poster_image = None
            self.root.after(0, lambda: self.poster_lab.config(image="", text="No Poster Loaded"))

    def update_poster_size(self):
        if not self.raw_poster_image: return
        pw, ph = self.preview.winfo_width() - 40, self.preview.winfo_height() - 130
        img = self.raw_poster_image.copy(); img.thumbnail((pw, ph), Image.Resampling.LANCZOS); self.current_poster = ImageTk.PhotoImage(img); self.poster_lab.config(image=self.current_poster, text="")

    def on_preview_resize(self, event):
        if self.raw_poster_image: self.update_poster_size()

    def open_trailer(self):
        if self.current_trailer_url: webbrowser.open(self.current_trailer_url)

    def clear_auth_fields(self):
        self.username_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")

    def confirm_logout(self):
        if messagebox.askyesno("Logout", "Confirm log out?"): self.show_login_page()

    def show_profile_menu(self, event):
        menu_commands = {
            'profile': self.show_profile_view,
            'settings': self.show_settings_page,
            'logout': self.confirm_logout
        }
        menu = ui_helpers.create_profile_menu(
            self.root, 
            self.colors, 
            self.font, 
            menu_commands
        )
        menu.post(event.x_root, event.y_root)

    def attempt_login(self, event=None):
        u = self.username_var.get()
        p = self.password_var.get()
        user = database.verify_user_login(u, p)

        if user:
            self.current_user_id = user['id']
            self.current_username = user['username']
            self.show_main_app()
        else:
            messagebox.showerror("Error", "Invalid Login. Please check your username and password.")

    def attempt_register(self, event=None):
        u = self.username_var.get().strip()
        p = self.password_var.get()
        cp = self.confirm_password_var.get()

        if not u or not p or not cp:
            return messagebox.showwarning("Warning", "All fields are required.")
        if len(u) < 5 or len(u) > 15:
            return messagebox.showwarning("Security", "Username must be 5-15 characters.")
        if len(p) < 8:
            return messagebox.showwarning("Security", "Password too weak! Minimum 8 characters.")
        if p != cp:
            return messagebox.showerror("Error", "Passwords do not match.")
        success, message = database.register_user(u, p)

        if success:
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login_page()
        else:
            messagebox.showerror("Registration Failed", message)

    def show_similar_movies_popup(self):
        recommendations_view.RecommendationsView(self).show()

    def _render_rec_list(self, parent, loader, recs):
        loader.destroy()
        
        if not recs:
            tk.Label(parent, text="No similar movies found.", bg=self.colors['secondary_bg'], 
                     fg="gray", font=('Segoe UI', 11)).pack(pady=20)
            return

        canvas = tk.Canvas(parent, bg=self.colors['secondary_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['secondary_bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for movie in recs:
            row = tk.Frame(scrollable_frame, bg=self.colors['input_bg'], pady=12)
            row.pack(fill="x", pady=5, padx=10)
            
            text_frame = tk.Frame(row, bg=self.colors['input_bg'])
            text_frame.pack(side="left", fill="both", expand=True, padx=(15, 5))

            full_date = movie.get('release_date', '')
            year = f"({full_date[:4]})" if full_date else ""
            movie_title = movie.get('title', 'Unknown Title')

            tk.Label(text_frame, 
                     text=f"{movie_title} {year}", 
                     bg=self.colors['input_bg'], fg="white", 
                     font=('Segoe UI', 10, 'bold'), 
                     anchor="w", 
                     justify="left",
                     wraplength=300).pack(fill="x")
            
            btn_frame = tk.Frame(row, bg=self.colors['input_bg'])
            btn_frame.pack(side="right", padx=15)

            tk.Button(btn_frame, 
                      text="+ ADD TO LIST", 
                      bg=self.colors['add_button'], 
                      fg="black", 
                      font=('Segoe UI', 8, 'bold'), 
                      padx=12, 
                      pady=6, 
                      relief="flat", 
                      cursor="hand2",
                      command=lambda m=movie: self._direct_add(m)).pack()
                      
        parent.winfo_toplevel().protocol("WM_DELETE_WINDOW", 
            lambda: (canvas.unbind_all("<MouseWheel>"), parent.winfo_toplevel().destroy()))

    def _direct_add(self, movie):
        title = movie['title']
        year = movie.get('release_date', '')[:4]
        status = "To Watch"
        remarks = "Added from Recommendations"

        ui_helpers.add_movie_logic(
            self.current_user_id, 
            title, 
            year, 
            status, 
            remarks, 
            self.refresh_table, 
            self.clear_fields
        )
        print(f"Success", f"'{title}' added successfully!")

    def _quick_fill(self, movie_data):
        self.title_var.set(movie_data['title'])
        self.release_year_var.set(movie_data['release_date'][:4])
        messagebox.showinfo("Quick Fill", f"'{movie_data['title']}' added to entry fields!")

if __name__ == "__main__":
    root = tk.Tk(); app = MovieManagementSystem(root); root.mainloop()