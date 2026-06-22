import requests
from PIL import Image
import io

def getImage(save_path="ultima_foto.jpg"):
    url = "http://192.168.0.39/capture"   # ← mude pro IP do seu ESP32
    
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        # Salva a imagem
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        # Carrega direto na memória (para processamento)
        image = Image.open(io.BytesIO(response.content))
        print(f"✅ Foto recebida! Tamanho: {image.size}")
        return image
    else:
        print("❌ Erro ao tirar foto")
        return None

# Uso
if __name__ == "__main__":
    img = getImage()
    if img:
        img.show()        # abre a imagem
        # img.save("placa.jpg")  # salva