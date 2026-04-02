import qrcode
from PIL import Image

# URL del sito
url = "https://bimegl.pythonanywhere.com/"

# Colore QR in RGB
colore_qr = (87, 130, 121)  # il tuo #578279

# Genera QR code
qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=4
)
qr.add_data(url)
qr.make(fit=True)

# Genera immagine in bianco e nero
img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

# Rendi trasparente lo sfondo bianco
datas = img.getdata()
new_data = []
for item in datas:
    if item[0] > 200 and item[1] > 200 and item[2] > 200:  # bianco
        new_data.append((255, 255, 255, 0))  # trasparente
    else:
        # Cambia il colore dei quadratini in colore_qr
        new_data.append((colore_qr[0], colore_qr[1], colore_qr[2], 255))
img.putdata(new_data)

# Salva in PNG (trasparenza supportata)
img.save("./static/images/qrcode.png")
print("QR code salvato con sfondo trasparente!")