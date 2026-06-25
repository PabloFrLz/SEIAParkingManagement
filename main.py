import requests
from PIL import Image, ImageEnhance, ImageFilter
import io
from paddleocr import PaddleOCR
import cv2
#import easyocrpi

SAVE_PATH = "img_placas/placa.png"
SAVE_PATH_2 = "img_placas/placa.png"
#SAVE_PATH_PROCESSED = "img_placas/processed_for_ocr.jpg"

    #  _______________________________________________________________________________________________________
    # |  DEPENDÊNCIAS:                                                                                        |
    # |     > python -m pip install paddlepaddle -i https://www.paddlepaddle.org.cn/packages/stable/cpu/      |
    # |     > pip install paddleocr                                                                           |
    # |_______________________________________________________________________________________________________|



# codigo teste - nao faz parte do SEIAParkingManagement até o momento
def getImage(save_path='placa.png'):
    url = "http://esp32cam.local/capture"   # ← mude pro IP do seu ESP32
    
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
    
    #  ___________________________
    # |         PaddleOCR         |
    # |___________________________|


def identificar_caracteres_com_paddleOCR():
    ocr = PaddleOCR(
        lang='en',
        text_detection_model_name="PP-OCRv6_server_det",
        text_recognition_model_name="PP-OCRv6_server_rec",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False
    )
    result = ocr.predict(SAVE_PATH)
    print("CARACTERES IDENTIFICADOS:\n")
    for res in result:
        texts = res["rec_texts"]
        scores = res["rec_scores"]
        for texto, score in zip(texts, scores):
            print(f"{texto}  (confiança: {score:.2f})")



    #  ___________________________
    # |         EasyOCR           |
    # |___________________________|

# Pré-processamento
'''def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Aumentar contraste
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    # Reduzir ruído
    gray = cv2.medianBlur(gray, 3)
    # Binarização
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    cv2.imwrite(SAVE_PATH_PROCESSED, thresh) # salva a imagem processada no diretorio
    return SAVE_PATH_PROCESSED # manda o endereço pro easyOCR



def identificar_caracteres_com_easyOCR():
    #processed = preprocess_image(SAVE_PATH_2)

    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(SAVE_PATH_2, detail=1)
    for detection in result:
        print(detection[1], f"Confiança: {detection[2]:.2f}")'''

'''reader = easyocr.Reader(['ch_tra', 'en'])
result = reader.readtext(SAVE_PATH)
print("CARACTERES IDENTIFICADOS:\n")
print(result)'''



# Uso
if __name__ == "__main__":
    img = getImage()
    if img:
        img.show()        # abre a imagem
        img.save(SAVE_PATH)  # salva
    
    identificar_caracteres_com_paddleOCR() # chama o metodo com o algoritmo de OCR
    #identificar_caracteres_com_easyOCR()