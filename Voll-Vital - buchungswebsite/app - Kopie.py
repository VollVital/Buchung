from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Ordner für Bewertungen, Avatare und Profilbilder
if not os.path.exists('bewertungen'):
    os.makedirs('bewertungen')
if not os.path.exists('static/avatars'):
    os.makedirs('static/avatars')
if not os.path.exists('static/profilbilder'):
    os.makedirs('static/profilbilder')

@app.route('/')
def home():
    return render_template('index.html')

# Vita-Seite
@app.route('/vita')
def vita():
    return render_template('vita.html')

# Profilbild-Upload für Vita-Seite
@app.route('/upload_profilbild', methods=['POST'])
def upload_profilbild():
    if 'profilbild' not in request.files:
        flash('Kein Bild ausgewählt')
        return redirect(url_for('vita'))
    file = request.files['profilbild']
    if file.filename == '':
        flash('Kein Bild ausgewählt')
        return redirect(url_for('vita'))
    if file:
        filename = file.filename
        file.save(os.path.join('static/profilbilder', filename))
        flash('Profilbild erfolgreich hochgeladen!')
    return redirect(url_for('vita'))

@app.route('/reputation')
def reputation():
    bewertungen = []
    sterne_gesamt = 0
    try:
        with open('bewertungen/bewertungen.txt', 'r', encoding='utf-8') as file:
            for line in file.readlines():
                parts = line.strip().split('|')
                if len(parts) == 5:
                    bewertungen.append({
                        'username': parts[0],
                        'sterne': int(parts[1]),
                        'kommentar': parts[2],
                        'zeitstempel': parts[3],
                        'avatar': parts[4]
                    })
                    sterne_gesamt += int(parts[1])
    except FileNotFoundError:
        pass
    durchschnitt = round(sterne_gesamt / len(bewertungen), 1) if bewertungen else 0
    return render_template('reputation.html', bewertungen=bewertungen, durchschnitt=durchschnitt)

@app.route('/bewertung_absenden', methods=['POST'])
def bewertung_absenden():
    username = request.form['username']
    sterne = request.form['stars']
    kommentar = request.form['kommentar']
    zeitstempel = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Zufälligen Avatar auswählen
    avatar = f"avatar{random.randint(1, 20)}.png"

    mitteilung = f"{username}|{sterne}|{kommentar}|{zeitstempel}|{avatar}\n"
    with open('bewertungen/bewertungen.txt', 'a', encoding='utf-8') as file:
        file.write(mitteilung)

    return redirect(url_for('reputation'))

# Shop-Seite
@app.route('/shop')
def shop():
    return render_template('shop.html')

# Trainings-Seite
@app.route('/training')
def training():
    return render_template('training.html')

# Buchungs-Seite
@app.route('/buchung')
def buchung():
    return render_template('buchung.html')

# Fehlerseite (404)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
