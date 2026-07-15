import requests
from PIL import Image #, ImageEnhance, ImageFilter
import io
#from paddleocr import PaddleOCR
#import cv2
import Recursos

class ModelPaddleOCR:
    def __init__(self):
        super().__init__()
        self.recursos = Recursos.Recursos()
        #url = "http://esp32cam.local/capture"   # insira o IP do servidor do ESP32
        self.url = "http://esp32cam.local/capture" # [v1.0.0.03]: URL onde o ESP32-S3-CAM WROOM conversa com a aplicação - o '/capture' força ele salvar o frame atual (bater uma foto)
        self.SAVE_PATH = "img_placas/placa.png" # [v1.0.0.03]: Diretório de armazenamento da imagem
        self.placa = [None, None] # [v1.0.0.03]: Armazena o número da placa e o percentual de confiança na predição (o quão confiante o modelo acredita estar)
        self.ocr = None # [v1.0.0.03]: Modelo usado para OCR (Reconhecimento Óptico de Caracter)    
        #SAVE_PATH_PROCESSED = "img_placas/processed_for_ocr.jpg"


    def getImage(self, save_path='placa.png'):
        #url = "http://esp32cam.local/capture"   # insira o IP do servidor do ESP32
        #url = "http://192.168.0.109/capture"
        
        response = requests.get(self.url, timeout=10)
        
        if response.status_code == 200:
            # Salva a imagem
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            # Carrega direto na memória (para processamento)
            image = Image.open(io.BytesIO(response.content))
            print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: ✅ Foto recebida! Tamanho: {image.size}")
            image = image.rotate(angle=270)
            return image
        else:
            print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: ❌ Erro ao tirar foto.")
            return None
        
        #  ___________________________
        # |         PaddleOCR         |
        # |___________________________|


    def identificar_caracteres_com_paddleOCR(self):
        self.ocr = PaddleOCR(
            text_detection_model_name="PP-OCRv5_server_det",
            text_recognition_model_name="PP-OCRv5_server_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )
        result = self.ocr.predict(self.SAVE_PATH)
        placa_moto = None
        print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: CARACTERES IDENTIFICADOS:\n")
        for res in result:
            texts = res["rec_texts"]
            scores = res["rec_scores"]
            for texto, score in zip(texts, scores):
                print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: {texto}  (confiança: {score:.2f})")
                if len(texto) == 3: # [v1.0.0.03]: extrai os 3 primeiros digitos da placa de moto (que não possuem o traço '-')
                    self.placa[0] = texto
                elif len(texto) == 4: # [v1.0.0.03]: extrai os 4 últimos digitos da placa de moto
                    self.placa[0] += f"-{texto}" # [v1.0.0.03]: concatena com os 3 digitos anteriores 
                elif (len(texto) == 7 or len(texto) == 8) and texto.replace('-', '').isalnum():  # [v1.0.0.03]: verifica se tem a quantidade de caracteres da placa MERCOSUL = depois verifica se tem a quantidade de caracteres da placa ANTIGA - por ultimo verifica se o texto é alfanumérico (o replace é pra tirar o traço pra nao dar erro na validação do isalnum()).
                    if "-" not in texto: # [v1.0.0.03]: verifica se o texto contém um traço, que é comum em placas de veículos ANTIGAS
                        self.placa[0] = f"{texto[:3]}-{texto[3:]}" # [v1.0.0.03]: salva a possível placa identificada com a adição do hífen '-' [P/ PLACAS MERCOSUL]
                    else:
                        self.placa[0] = texto # [v1.0.0.03]: salva a possível placa identificada (P/ PLACAS PADRÃO ANTIGO)
                        
                else:
                    self.placa[0] = f"|PLACA FORA DOS PADRÕES ESPERADOS: '{texto}' |" # [v1.0.0.03]: caso o texto identificado não se encaixe nos padrões de placas, ele é armazenado como uma possível placa inválida
                
                self.placa[1] = f"{score:.2f}" # [v1.0.0.03]: salva a probabilidade para a predição da placa




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
'''if __name__ == "__main__":
    model_ocr = ModelPaddleOCR()
    img = model_ocr.getImage()
    if img:
        img.show()        # [v1.0.0.03]: abre a imagem
        img.save(model_ocr.SAVE_PATH)  # [v1.0.0.03]: salva
    
    model_ocr.identificar_caracteres_com_paddleOCR() # [v1.0.0.03]: chama o metodo com o algoritmo de OCR usando PaddleOCR

    print("PLACA IDENTIFICADA:\n")
    print(" ___________________________\n")
    print(f"|    PLACA: {model_ocr.placa[0]}       |\n")
    print(f"|    CONFIANÇA: {str(float(model_ocr.placa[1])*100)}%       |\n")
    print("|___________________________|\n")
'''
    #identificar_caracteres_com_easyOCR()