import tkinter as tk
import api_handler
import ui_helpers

class ProfileView:
    # Initialize the profile view with container (parent frame) and controller (app logic reference).
    def __init__(self, container, controller):
        self.container = container
        self.controller = controller
        self.colors = controller.colors

    # Render the full profile view including header, profile photo, username, and stats.
    def render(self):
        self.controller._clear_view()
        
        header = tk.Frame(self.container, bg=self.colors['primary_bg'], pady=20)
        header.pack(fill="x", padx=40)
        
        tk.Button(header, text="← HOME", font=self.controller.font_bold, 
                  bg=self.colors['primary_accent'], fg="white", relief="flat", 
                  padx=15, command=self.controller.show_main_app, cursor="hand2").pack(side="left")
        
        main_frame = tk.Frame(self.container, bg=self.colors['primary_bg'])
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        left_side = tk.Frame(main_frame, bg=self.colors['primary_bg'], padx=40)
        left_side.pack(side="left", fill="both", expand=True)

        photo_center_f = tk.Frame(left_side, bg=self.colors['primary_bg'])
        photo_center_f.pack(expand=True)

        photo_container = tk.Frame(photo_center_f, width=160, height=160, bg=self.colors['primary_bg'])
        photo_container.pack()
        photo_container.pack_propagate(False)

        p_img = self.controller.get_profile_image()
        if p_img:
            img_lab = tk.Label(photo_container, image=p_img, bg=self.colors['primary_bg'])
            img_lab.image = p_img
            img_lab.pack(fill="both", expand=True)
        else:
            canvas = tk.Canvas(photo_container, width=160, height=160, 
                               bg=self.colors['primary_bg'], highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.create_oval(5, 5, 155, 155, outline="white", width=4)
            canvas.create_text(80, 80, text="👤", font=('Segoe UI', 80), fill="white")

        tk.Label(photo_center_f, text=self.controller.current_username, 
                 font=('Segoe UI', 24, 'bold'), bg=self.colors['primary_bg'], 
                 fg=self.colors['primary_accent']).pack(pady=15)

        right_side = tk.Frame(main_frame, bg=self.colors['primary_bg'], padx=40)
        right_side.pack(side="right", fill="both", expand=True)
        
        stats = api_handler.get_movie_stats(self.controller.current_user_id, self.controller.database_module)
        self._render_stats_box(right_side, stats)

    # Render a stats box displaying tracked movies and status counts.
    def _render_stats_box(self, parent, stats):
        stats_box = tk.Frame(parent, bg=self.colors['secondary_bg'], padx=30, pady=30, 
                             highlightbackground="white", highlightthickness=1)
        stats_box.pack(pady=20)

        def add_stat(label_text, value, color="white"):
            row = tk.Frame(stats_box, bg=self.colors['secondary_bg'])
            row.pack(fill="x", pady=5)
     
            lbl = tk.Label(row, text=label_text, font=('Segoe UI', 10), 
                           bg=self.colors['secondary_bg'], fg="lightgray", 
                           width=20, anchor='w')
            lbl.pack(side="left")
            
            val = tk.Label(row, text=str(value), font=('Segoe UI', 11, 'bold'), 
                           bg=self.colors['secondary_bg'], fg=color)
            val.pack(side="right", padx=(20,0))

        add_stat("🎬 Total Movies Tracked:", stats['total'], self.colors['primary_accent'])
        add_stat("⭐ Favorite Genre:", stats['fav_genre'], "#FFE28B")
        
        tk.Frame(stats_box, height=1, bg="gray").pack(fill="x", pady=10)
        
        status_items = [
            ("Completed", "🏆 Completed:", self.colors['add_button']),
            ("Watching", "▶️ Watching:", self.colors['primary_accent']),
            ("On Hold", "⏸️ On Hold:", self.colors['update_button']),
            ("To Watch", "📌 To Watch:", "white")
        ]
        
        for key, display_label, color in status_items:
            count = stats['status_counts'].get(key, 0)
            add_stat(display_label, count, color)
            
        add_stat("❓ No Status Set:", stats['no_status'], self.colors['delete_button'])
        
        # Logout Button
        tk.Button(stats_box, text="LOG OUT", font=self.controller.font_bold, 
                  bg=self.colors['delete_button'], fg="white", relief="flat", 
                  command=self.controller.confirm_logout, cursor="hand2").pack(pady=(20, 0), fill="x")