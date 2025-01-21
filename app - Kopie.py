from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import boto3
from botocore.exceptions import NoCredentialsError

# Umgebungsvariablen laden
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET = os.getenv('S3_BUCKET')

# S3-Client konfigurieren
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Ordner für Bewertungen, Avatare und Profilbilder (Doppelte Erstellung entfernt)
os.makedirs('bewertungen', exist_ok=True)
os.makedirs('static/avatars', exist_ok=True)
os.makedirs('static/profilbilder', exist_ok=True)

# 🏠 Startseite (Fehlende Route hinzugefügt)
@app.route('/')
def home():
    return render_template('index.html')

# 👤 Vita-Seite
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

    bewertungen = sorted(bewertungen, key=lambda x: x['zeitstempel'], reverse=True)
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

# Produkt-Detailseite
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # Beispielhafte Produktdaten
    produkte = {
        1: {
            'name': 'Faszienrolle Pro',
            'beschreibung': 'Intensive Tiefengewebemassage zur Regeneration.',
            'preis': '29,99€',
            'bilder': [
                'shop/produkt1_main.jpg',
                'shop/produkt1_1.jpg',
                'shop/produkt1_2.jpg',
                'shop/produkt1_3.jpg',
                'shop/produkt1_4.jpg'
            ]
        },
        2: {
            'name': 'Massagepistole X',
            'beschreibung': 'Vielseitige Anwendung zur Muskelentspannung.',
            'preis': '89,99€',
            'bilder': [
                'shop/produkt2_main.jpg',
                'shop/produkt2_1.jpg',
                'shop/produkt2_2.jpg',
                'shop/produkt2_3.jpg',
                'shop/produkt2_4.jpg'
            ]
        },
        3: {
            'name': 'Faszienball Duo',
            'beschreibung': 'Gezielte Triggerpunkt-Massage.',
            'preis': '14,99€',
            'bilder': [
                'shop/produkt3_main.jpg',
                'shop/produkt3_1.jpg',
                'shop/produkt3_2.jpg',
                'shop/produkt3_3.jpg',
                'shop/produkt3_4.jpg'
            ]
        },
        4: {
            'name': 'Vibrationsplatte V2',
            'beschreibung': 'Für effektives Ganzkörpertraining.',
            'preis': '199,99€',
            'bilder': [
                'shop/produkt4_main.jpg',
                'shop/produkt4_1.jpg',
                'shop/produkt4_2.jpg',
                'shop/produkt4_3.jpg',
                'shop/produkt4_4.jpg'
            ]
        },
        5: {
            'name': 'Faszienband Stretch',
            'beschreibung': 'Perfekt für Dehnübungen und Mobilität.',
            'preis': '19,99€',
            'bilder': [
                'shop/produkt5_main.jpg',
                'shop/produkt5_1.jpg',
                'shop/produkt5_2.jpg',
                'shop/produkt5_3.jpg',
                'shop/produkt5_4.jpg'
            ]
        }
    }

    produkt = produkte.get(product_id)
    if produkt:
        return render_template('product_detail.html', produkt=produkt)
    else:
        return redirect(url_for('shop'))

# Trainings-Seite
@app.route('/training')
def training():
    return render_template('training.html')

# Buchungs-Seite
@app.route('/buchung')
def buchung():
    return render_template('buchung.html')

# Ordner für Bewertungen, Avatare und Profilbilder
os.makedirs('bewertungen', exist_ok=True)
os.makedirs('static/avatars', exist_ok=True)
os.makedirs('static/profilbilder', exist_ok=True)

# Impressum-Seite
@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

# Route für das Kontaktformular (Korrigiert)
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # E-Mail-Konfiguration
    sender_email = "info.vollvital@gmail.com"
    receiver_email = "info.vollvital@gmail.com"
    password = "dtdq gnhc jyxe dwun"  # Sicheres Passwort nutzen

    subject = f"Neue Nachricht von {name}"
    body = f"Name: {name}\nE-Mail: {email}\n\nNachricht:\n{message}"

    # E-Mail vorbereiten
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Verbindung zum Gmail SMTP-Server herstellen
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        flash('Nachricht erfolgreich gesendet!', 'success')
    except Exception as e:
        print(f"Fehler beim Senden der Nachricht: {e}")
        flash('Fehler beim Senden der Nachricht. Bitte versuchen Sie es später erneut.', 'danger')

    return redirect(url_for('impressum'))


if __name__ == '__main__':
    app.run(debug=True)

# Fehlerseite (404)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404