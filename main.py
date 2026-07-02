# build.py
data = {
    "name": "RAJ MODS",
    "age": "20",
    "location": "Rajasthan, India",
    "skills": ["Python", "JavaScript", "Firebase", "UI/UX Design", "Encryption"],
    "bio": "Expert in high-security app development and aesthetic UI design."
}

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ background: #1a1a1a; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .portfolio-card {{ background: #2d2d2d; padding: 40px; border-radius: 20px; border: 2px solid #333; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 350px; text-align: center; }}
        h1 {{ color: #00ffcc; margin-bottom: 10px; }}
        .skill-tag {{ display: inline-block; background: #333; padding: 5px 15px; margin: 5px; border-radius: 15px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="portfolio-card">
        <h1>{data['name']}</h1>
        <p>Age: {data['age']} | {data['location']}</p>
        <hr>
        <p>{data['bio']}</p>
        <div>
            {"".join([f'<span class="skill-tag">{s}</span>' for s in data['skills']])}
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_content)
    print("Portfolio successfully generated: index.html")
