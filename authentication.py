import tkinter as tk
import ui_helpers
from tkinter import messagebox
import database

class Authentication:
    def __init__(self, container, controller):
        # Initialize with main container and app controller reference.
        self.container = container
        self.controller = controller
        self.colors = controller.colors

    # Create a labeled input field with optional password masking.
    # Includes an icon on the left side.
    def _create_auth_entry(self, parent, label, var, icon, is_pass=False):
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg=self.colors['primary_bg'], fg="white", anchor='w').pack(fill='x', pady=(10, 0))
        f = tk.Frame(parent, bg="white", padx=5, pady=2)
        f.pack(fill='x', pady=2)
        tk.Label(f, text=icon, font=('Segoe UI', 12), bg="white", fg="gray").pack(side='left')
        e = tk.Entry(f, textvariable=var, font=('Segoe UI', 11), bg="white", fg="black", relief='flat', bd=0)
        if is_pass: e.config(show="*")
        e.pack(side='left', fill='x', expand=True, padx=5)

    # Render the login page with username/password fields and action buttons.
    def render_login(self):
        frame = tk.Frame(self.container, bg=self.colors['primary_bg'])
        frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(frame, text="🎬CINETRACK", font=('Segoe UI', 32, 'bold'), bg=self.colors['primary_bg'], fg="white").pack(pady=20)
        box = tk.Frame(frame, bg=self.colors['primary_bg'], highlightbackground="white", highlightthickness=1, padx=50, pady=40)
        box.pack()
        tk.Label(box, text="Welcome back!", font=('Segoe UI', 18, 'bold'), bg=self.colors['primary_bg'], fg="white").pack(pady=(0, 30))
        self._create_auth_entry(box, "Username:", self.controller.username_var, "👤")
        self._create_auth_entry(box, "Password:", self.controller.password_var, "🔒", True)
        tk.Button(box, text="Log in", command=self.controller.attempt_login, font=('Segoe UI', 11, 'bold'), bg=self.controller.colors['add_button'], fg="black", relief='flat', width=20, cursor="hand2").pack(pady=25)
        tk.Button(box, text="Create an Account", command=self.controller.show_register_page, font=('Segoe UI', 9, 'underline'), bg=self.colors['primary_bg'], fg="white", borderwidth=0, cursor="hand2").pack()

    # Render the registration page with username/password fields and action buttons.
    def render_register(self):
        frame = tk.Frame(self.container, bg=self.colors['primary_bg'])
        frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(frame, text="REGISTER", font=('Segoe UI', 32, 'bold'), bg=self.colors['primary_bg'], fg="white").pack(pady=20)
        box = tk.Frame(frame, bg=self.colors['primary_bg'], highlightbackground="white", highlightthickness=1, padx=50, pady=40)
        box.pack()
        self._create_auth_entry(box, "Username:", self.controller.username_var, "👤")
        self._create_auth_entry(box, "Password:", self.controller.password_var, "🔒", True)
        self._create_auth_entry(box, "Confirm Password:", self.controller.confirm_password_var, "🔒", True)
        tk.Button(box, text="Sign Up", command=self.controller.attempt_register, font=('Segoe UI', 11, 'bold'), bg=self.controller.colors['add_button'], fg="black", relief='flat', width=20, cursor="hand2").pack(pady=20)
        tk.Button(box, text="Back to Login", command=self.controller.show_login_page, font=('Segoe UI', 9, 'underline'), bg=self.colors['primary_bg'], fg="white", borderwidth=0, cursor="hand2").pack()

    # Open a popup window for changing the username securely.
    def open_change_username_popup(self):
        win = tk.Toplevel(self.controller.root)
        win.withdraw()
        win.title("Account Settings")
        win.configure(bg=self.colors['secondary_bg'])
        win.resizable(False, False)
        
        ui_helpers.center_window(win, 450, 300)

        curr_p, new_u, confirm_p = tk.StringVar(), tk.StringVar(), tk.StringVar()

        tk.Label(win, text="CHANGE USERNAME", font=('Segoe UI', 18, 'bold'), 
                bg=self.colors['secondary_bg'], fg="white").pack(pady=(30, 20))

        input_container = tk.Frame(win, bg=self.colors['secondary_bg'])
        input_container.pack(fill="x", padx=40)
        input_container.grid_columnconfigure(0, weight=1)
        input_container.grid_columnconfigure(3, weight=1)

        ui_helpers.create_input_field(input_container, "New Username:", new_u, 0, 
                             self.controller.font_bold, self.controller.font, self.colors)
        ui_helpers.create_input_field(input_container, "Password:", curr_p, 1, 
                                    self.controller.font_bold, self.controller.font, self.colors, show="*")
        ui_helpers.create_input_field(input_container, "Re-enter Password:", confirm_p, 2, 
                                    self.controller.font_bold, self.controller.font, self.colors, show="*")
        tk.Button(win, 
                  text="Update", 
                  font=self.controller.font_bold, 
                  width=20,                    
                  bg=self.colors['primary_accent'], 
                  fg="white", 
                  relief="flat", 
                  padx=15,                     
                  cursor="hand2",
                  command=lambda: self.process_username_update(curr_p.get(), new_u.get(), confirm_p.get(), win)
                  ).pack(pady=40)
        
        win.deiconify()
        win.grab_set()

    # Open a popup window for changing the password securely.
    def open_change_password_popup(self):
        win = tk.Toplevel(self.controller.root)
        win.withdraw()
        win.title("Update Password")
        win.configure(bg=self.colors['secondary_bg'])
        win.resizable(False, False)
        
        ui_helpers.center_window(win, 450, 300)

        curr_p, new_p, confirm_p = tk.StringVar(), tk.StringVar(), tk.StringVar()

        tk.Label(win, text="CHANGE PASSSWORD", font=('Segoe UI', 18, 'bold'), 
                bg=self.colors['secondary_bg'], fg="white").pack(pady=(30, 20))

        input_container = tk.Frame(win, bg=self.colors['secondary_bg'])
        input_container.pack(fill="x", padx=40)
        input_container.grid_columnconfigure(0, weight=1)
        input_container.grid_columnconfigure(3, weight=1)

        ui_helpers.create_input_field(input_container, "Current Password:", curr_p, 0, 
                             self.controller.font_bold, self.controller.font, self.colors, show="*")
        ui_helpers.create_input_field(input_container, "New Password:", new_p, 1, 
                                    self.controller.font_bold, self.controller.font, self.colors, show="*")
        ui_helpers.create_input_field(input_container, "Re-enter New Password:", confirm_p, 2, 
                                    self.controller.font_bold, self.controller.font, self.colors, show="*")

        tk.Button(win, 
                  text="Update", 
                  font=self.controller.font_bold, 
                  width=20,                     
                  bg=self.colors['primary_accent'], 
                  fg="white", 
                  relief="flat", 
                  padx=15, 
                  cursor="hand2",
                  command=lambda: self.process_password_update(curr_p.get(), new_p.get(), confirm_p.get(), win)
                  ).pack(pady=40)
        
        win.deiconify()
        win.grab_set()
          
    # Render the account settings page with security and data options.
    def render_settings(self):
        header = tk.Frame(self.container, bg=self.colors['primary_bg'], pady=20) 
        header.pack(fill="x", padx=40)

        tk.Button(header, text="← HOME", font=self.controller.font_bold, 
                bg=self.colors['primary_accent'], fg="white", relief="flat", 
                padx=15, command=self.controller.show_main_app, cursor="hand2").pack(side="left")
        
        main_frame = tk.Frame(self.container, bg=self.colors['primary_bg'])
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        box = tk.Frame(main_frame, bg=self.colors['secondary_bg'], padx=40, pady=40, 
                    highlightbackground="white", highlightthickness=1)
        box.pack()

        tk.Label(box, text="ACCOUNT SECURITY", font=self.controller.font_bold, 
                bg=self.colors['secondary_bg'], fg="white").pack(pady=(0,10))
        
        tk.Button(box, text="Change Username", font=self.controller.font, width=30, 
                bg=self.colors['input_bg'], fg="white", relief="flat", cursor="hand2", 
                command=self.controller.open_change_username).pack(pady=5)
        
        tk.Button(box, text="Change Password", font=self.controller.font, width=30, 
                bg=self.colors['input_bg'], fg="white", relief="flat", cursor="hand2", 
                command=self.controller.open_change_password).pack(pady=5)
        
        tk.Button(box, text="Update Profile Photo", font=self.controller.font, width=30, 
                bg=self.colors['input_bg'], fg="white", relief="flat", cursor="hand2", 
                command=self.controller.change_profile_photo).pack(pady=5)
        
        tk.Button(box, text="Remove Profile Photo", font=self.controller.font, width=30, 
                bg=self.colors['delete_button'], fg="black", relief="flat", cursor="hand2", 
                command=self.controller.remove_profile_photo).pack(pady=5)

        tk.Frame(box, height=1, bg="gray", width=250).pack(pady=20)

        tk.Label(box, text="DOWNLOAD DATA", font=self.controller.font_bold, 
                bg=self.colors['secondary_bg'], fg="white").pack(pady=(0,10))
        
        tk.Button(box, text="PDF Report", font=self.controller.font, width=30, 
                bg=self.colors['add_button'], fg="black", relief="flat", cursor="hand2", 
                command=self.controller.export_as_pdf).pack(pady=5)
        
        tk.Button(box, text="CSV Report", font=self.controller.font, width=30, 
                bg=self.colors['update_button'], fg="black", relief="flat", cursor="hand2", 
                command=self.controller.export_as_csv).pack(pady=5)
        
    # Process changing username.
    # Validates input, checks confirmation, updates DB, and logs out user.
    def process_username_update(self, current_pass, new_username, confirm_pass, win):
        trimmed_u = new_username.strip()
        if not current_pass or not trimmed_u or not confirm_pass:
            return messagebox.showwarning("Warning", "All fields are required.")
        if trimmed_u == self.controller.current_username:
            return messagebox.showwarning("Security", f"You are already using '{trimmed_u}'. Choose a different one.")  
        if len(trimmed_u) < 5 or len(trimmed_u) > 15:
            return messagebox.showwarning("Security", "Username must be 5-15 characters.")    
        if not messagebox.askyesno("Confirm", f"Change username to '{trimmed_u}' and logout?"):
            return

        success, message = database.update_username_secure(
            self.controller.current_user_id, 
            current_pass, 
            trimmed_u
        )
        
        if success:
            if win.winfo_exists():
                win.grab_release()
                win.destroy()
            messagebox.showinfo("Success", "Username changed! Please log in again.")
            self.controller.show_login_page()
        else:
            messagebox.showerror("Error", message)

    # Process changing password.
    # Validates input, confirms action, updates DB, and logs out user.
    def process_password_update(self, current_pass, new_pass, confirm_pass, win):
        if not current_pass or not new_pass or not confirm_pass:
            return messagebox.showwarning("Warning", "All fields are required.")
        if len(new_pass) < 8:
            return messagebox.showwarning("Security", "Password too weak! Minimum 8 characters.")
        if new_pass != confirm_pass:
            return messagebox.showerror("Mismatch", "New passwords do not match.")
        confirm = messagebox.askyesno("Confirm", "Are you sure? You will be logged out.")
        
        if confirm:
            success, message = database.update_password_secure(
                self.controller.current_user_id, 
                current_pass, 
                new_pass
            )
            if success:
                win.destroy()
                messagebox.showinfo("Success", "Password updated! Please log in again.")
                self.controller.show_login_page()
            else:
                messagebox.showerror("Error", message)