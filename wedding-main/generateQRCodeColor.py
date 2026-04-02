import qrcode
from PIL import Image

# L'URL del tuo sito
url = "https://bimegl.pythonanywhere.com/"

# Colore personalizzato in RGB
colore_qr = (87, 130, 121)        # rosso
colore_sfondo = (255, 255, 255) # bianco

# Genera il QR code
qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=4
)
qr.add_data(url)
qr.make(fit=True)

# Crea immagine con colori RGB
img = qr.make_image(fill_color=colore_qr, back_color=None).convert('RGB')

# Salva il QR code
img.save("/static/images/qrcode.png")
print("QR code salvato come qrcode_color.png")