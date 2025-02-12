from flask import Flask, render_template, jsonify, abort
import json
import os
import pandas as pd

app = Flask(__name__)

# Load letters metadata from letters.json dynamically
def load_letters():
    if os.path.exists("letters.json"):
        with open("letters.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):  # Ensure data is a list of letters
                    print("Error: letters.json is not in the correct format.")
                    return []
                return data
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in letters.json")
                return []
    else:
        print("Warning: letters.json not found. Did you run parse_tei.py?")
        return []

@app.route("/")
def index():
    """
    Show an index page listing all letters from letters.json.
    """
    letters_data = load_letters()
    
    # Ensure date sorting works with missing dates
    sorted_letters = sorted(letters_data, key=lambda x: x.get('date', '9999-12-31'))
    
    # If you have at least one letter, derive the seriesTitle from it
    if sorted_letters:
        raw_series_title = sorted_letters[0].get("seriesTitle", "")
        # Tidy up newlines or extra spaces:
        series_title = raw_series_title.replace('\n', ' ').strip()
    else:
        # Fallback if no letters exist
        series_title = "Digital Scholarly Edition"

    return render_template("index.html",
                           letters=sorted_letters,
                           seriesTitle=series_title)  # <--- pass to template

@app.route("/letter/<letter_id>")
def letter_view(letter_id):
    letters_data = load_letters()
    letter = next((l for l in letters_data if l["id"] == letter_id), None)
    if not letter:
        abort(404)

    # Derive the series title from this letter or a default
    raw_title = letter.get("seriesTitle", "")
    series_title = raw_title.replace('\n', ' ').strip() or "Digital Scholarly Edition"

    return render_template(
        "letter_view.html",
        letter=letter,
        seriesTitle=series_title  # Pass the title explicitly
    )

# ==========================
# TIMELINE FUNCTIONALITY
# ==========================

@app.route("/timeline")
def timeline():
    letters_data = load_letters()
    # Example: get seriesTitle from the first letter, or just define it yourself:
    if letters_data:
        raw_title = letters_data[0].get("seriesTitle", "")
        series_title = raw_title.replace('\n', ' ').strip()
    else:
        series_title = "Digital Scholarly Edition"

    return render_template("timeline.html", seriesTitle=series_title)

@app.route("/timeline_data")
def timeline_data():
    """
    Provide aggregated letter data (letters per month) for visualization.
    """
    letters_data = load_letters()

    if not letters_data:
        return jsonify({"dates": [], "letters": []})

    # Convert to DataFrame
    df = pd.DataFrame(letters_data)

    # Ensure 'date' is valid
    if 'date' not in df or df.empty:
        return jsonify({"dates": [], "letters": []})

    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Remove invalid dates
    df = df.dropna(subset=['date'])

    if df.empty:
        return jsonify({"dates": [], "letters": []})

    # Group by year-month and count letters
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    letter_counts = df.groupby('year_month').size().reset_index(name='letters')

    # Convert to JSON
    return jsonify({
        "dates": letter_counts['year_month'].tolist(),
        "letters": letter_counts['letters'].tolist()
    })

if __name__ == "__main__":
    app.run(debug=True, extra_files=["letters.json"])
