
from PIL import Image
from paddleocr import PaddleOCR
import subprocess
import Recursos
import os


class ModelPaddleOCR:
    def __init__(self):
        super().__init__()
        self.recursos = Recursos.Recursos()
        self.url = "rtsp://admin:password@127.0.0.1:554/onvif1" # [v1.0.0.03]: URL onde ocorrerá a comunicação entre aplicação e câmera IP
        output_dir = "img_placas"
        os.makedirs(output_dir, exist_ok=True)  # cria o diretorio "img_placas" caso não exista, e não reclama se já existir
        self.SAVE_PATH = os.path.join(output_dir, "frame_capture.jpg") # [v1.0.0.03]: Diretório de armazenamento da imagem
        self.placa = [None, None] # [v1.0.0.03]: Armazena o número da placa e o percentual de confiança na predição (o quão confiante o modelo acredita estar)
        self.ocr = None # [v1.0.0.03]: Modelo usado para OCR (Reconhecimento Óptico de Caracter)    


    #  _____________________________________
    # |         Capturando um frame         |
    # |_____________________________________|

    def getImage(self):
        try:
            # [v1.0.0.03]: Captura a imagem usando ffmpeg
            subprocess.run([
                "ffmpeg", "-y",
                "-i", self.url,
                "-frames:v", "1",
                "-q:v", "2",
                self.SAVE_PATH
            ], check=True)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: ❌ Falha ao capturar frame via ffmpeg: {e}")
            return None
        
        image = Image.open(self.SAVE_PATH) # [v1.0.0.03]: carrega a imagem

        if image is not None:
            print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: ✅ Imagem carregada! Tamanho: {image.size}")
            #  ________________________________
            # |        ROTAÇÃO DA IMAGEM       |
            # |________________________________|
            # [v1.0.0.03]: rotaciona a imagem em 270ºC
            #image = image.rotate(angle=270) 

            return image
        else:
            print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: ❌ Erro ao carregar imagem.")
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

        print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: CARACTERES IDENTIFICADOS:\n")
        for res in result:
            texts = res["rec_texts"]
            scores = res["rec_scores"]
            for texto, score in zip(texts, scores):
                print(f"[{self.recursos.CORES.AMARELO}ModelPaddleOCR.py{self.recursos.CORES.RESET}]: {texto}  (confiança: {score:.2f})")
                if len(texto) == 3: # [v1.0.0.03]: extrai os 3 primeiros digitos da placa de moto (que não possuem o traço '-')
                    self.placa[0] = texto
                    # [v1.0.0.03]: nao da return pois precisa pegar os 4 digitos restantes
                elif len(texto) == 4: # [v1.0.0.03]: extrai os 4 últimos digitos da placa de moto
                    self.placa[0] += f"-{texto}" # [v1.0.0.03]: concatena com os 3 digitos anteriores 
                    return # [v1.0.0.03]: da return pois já tem a placa de moto completa
                elif (len(texto) == 7 or len(texto) == 8) and texto.replace('-', '').isalnum():  # [v1.0.0.03]: verifica se tem a quantidade de caracteres da placa MERCOSUL = depois verifica se tem a quantidade de caracteres da placa ANTIGA - por ultimo verifica se o texto é alfanumérico (o replace é pra tirar o traço pra nao dar erro na validação do isalnum()).
                    if "-" not in texto: # [v1.0.0.03]: verifica se o texto contém um traço, que é comum em placas de veículos ANTIGAS
                        self.placa[0] = f"{texto[:3]}-{texto[3:]}" # [v1.0.0.03]: salva a possível placa identificada com a adição do hífen '-' [P/ PLACAS MERCOSUL]
                    else:
                        self.placa[0] = texto # [v1.0.0.03]: salva a possível placa identificada (P/ PLACAS PADRÃO ANTIGO)     
                    return # [v1.0.0.03]: retorna a placa   
                else:
                    self.placa[0] = f" FORA DOS PADRÕES ESPERADOS: '{texto}' " # [v1.0.0.03]: caso o texto identificado não se encaixe nos padrões de placas, ele é armazenado como uma possível placa inválida
                
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

