import tkinter as tk
from tkinter import ttk, messagebox
import threading
import api_handler
import ui_helpers

class RecommendationsView:
    def __init__(self, controller):
    # Initialize with reference to main controller (MovieManagementSystem)
        self.controller = controller
        self.root = controller.root
        self.colors = controller.colors

    def show(self):
    # Display the recommendations popup for the currently selected movie.
    # Fetches similar movies asynchronously and renders them in a scrollable list.
        if not self.controller.selected_id:
            return messagebox.showwarning("Selection", "Please select a movie first!")

        selected_item = self.controller.movie_table.item(self.controller.movie_table.selection()[0], 'values')
        movie_title = selected_item[1]

        # Create popup window
        win = tk.Toplevel(self.root)
        win.withdraw()
        win.title(f"More Like {movie_title}")
        win.minsize(500, 600)
        ui_helpers.center_window(win, 500, 600)
        win.configure(bg=self.colors['secondary_bg'])
        win.grab_set()

        # Header label
        tk.Label(win, text="MORE LIKE THIS", font=('Segoe UI', 18, 'bold'), 
                 bg=self.colors['secondary_bg'], fg="white").pack(pady=(30, 20))
        container = tk.Frame(win, bg=self.colors['secondary_bg'])
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # Loader while fetching
        loader = tk.Label(container, text="Searching...", bg=self.colors['secondary_bg'], fg="white")
        loader.pack(pady=50)

        # Fetch recommendations in a separate thread
        def run_search():
            recs = api_handler.get_similar_movies(movie_title)
            self.root.after(0, lambda: self._render_list(container, loader, recs, win))

        threading.Thread(target=run_search, daemon=True).start()
        win.deiconify()

    def _render_list(self, parent, loader, recs, win):
        # Render the list of recommended movies in the popup.
        # Supports scrollable canvas and "+ ADD" buttons for each recommendation.
        loader.destroy()
        
        if not recs:
            tk.Label(parent, text="No similar movies found.", bg=self.colors['secondary_bg'], 
                     fg="gray", font=('Segoe UI', 11)).pack(pady=20)
            return

        # Scrollable canvas setup
        canvas = tk.Canvas(parent, bg=self.colors['secondary_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['secondary_bg'])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Resize scrollable frame with canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add each recommended movie as a row with title and "+ ADD" button
        for movie in recs:
            row = tk.Frame(scrollable_frame, bg=self.colors['input_bg'], pady=12)
            row.pack(fill="x", pady=5, padx=10)

            text_frame = tk.Frame(row, bg=self.colors['input_bg'])
            text_frame.pack(side="left", fill="both", expand=True, padx=(15, 5))

            year = f"({movie.get('release_date', '')[:4]})" if movie.get('release_date') else ""
            tk.Label(text_frame, text=f"{movie['title']} {year}", bg=self.colors['input_bg'], 
                     fg="white", font=('Segoe UI', 10, 'bold'), anchor="w", 
                     justify="left", wraplength=250).pack(fill="x")

            # Button to add movie directly to list
            tk.Button(row, text="+ ADD", bg=self.colors['add_button'], fg="black", font=('Segoe UI', 8, 'bold'),
                      padx=10, pady=5, relief="flat", cursor="hand2",
                      command=lambda m=movie: self.controller._direct_add(m)).pack(side="right", padx=15)

        # Cleanup mousewheel binding on close
        win.protocol("WM_DELETE_WINDOW", lambda: (canvas.unbind_all("<MouseWheel>"), win.destroy()))