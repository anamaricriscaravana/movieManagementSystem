import csv

def save_to_csv(path, movie_data):
    # Save a list of movies to a CSV file.
    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Genre', 'Year', 'Status'])
        for m in movie_data:
            writer.writerow(list(m))

def save_to_pdf(path, movie_data):
    # Save a list of movies to a CSV file.
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Segeo UI-Bold", 16)
    c.drawString(50, 750, "MOVIE COLLECTION REPORT")
    
    y = 720
    c.setFont("Segeo UI", 10)
    for m in movie_data:
        c.drawString(50, y, f"{m[0]} ({m[1]}) - Status: {m[2]}")
        y -= 20
        
        if y < 50:
            c.showPage()
            y = 750
            c.setFont("Segeo UI", 10)
    c.save()