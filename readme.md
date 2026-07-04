
 # SEIA Parking Management v1.0.0.03
**Software de Controle de Estacionamento Institucional**  
Desenvolvido para o Núcleo Administrativo Setorial (NAS), vinculado à Secretaria da Inovação em Inteligência 
Artificial (SEIA), do estado do Paraná. **Arquivos com dados restritos da Secretaria foram omitidos, atendendo**
**ao que determina a LGPD.**


 ## Interfaces da Aplicação

![Tela do sistema 1](interface_da_aplicacao/img1.png)
![Tela do sistema 2](interface_da_aplicacao/img4.png)
![Tela do sistema 3](interface_da_aplicacao/img2.png)
![Tela do sistema 4](interface_da_aplicacao/img3.png)

 ## CONFIGURANDO O AMBIENTE

 ### DEPENDÊNCIAS NECESSÁRIAS:

```bash
winget install Python.Python.3.12
pip install pyside6
pip install pyqtdarktheme
pip install pymysql
pip install cryptography
pip install pypdf
pip install reportlab
```

 ## CONFIGURANDO O BANCO:
	  NOTA: instalar o mysql server 8.0 e setar as variaveis de ambiente se for necessário.
	• Modificar as variaveis globais USER e PASSWORD do arquivo SEIAParkingManagement.py 
	  com as credenciais do seu banco de dados;
 	• Entrar no banco via cmd e executar os códigos:
```bash
source C:(caminho_para_projeto)\SEIAParkingManagement\database\seia_parking.sql
source C:(caminho_para_projeto)\SEIAParkingManagement\database\autarquia.sql
source C:(caminho_para_projeto)\SEIAParkingManagement\database\vagas.sql
```
    • E depois carregar os demais dados no banco na seguinte sequencia:
```bash
// servidores.sql
// carros.sql
``` 
    • O ideal é que os dados de servidores sejam inseridos manualmente via aplicação.


 ## PREDIÇÃO DE PLACAS (OCR):
Para predição de placas, foi usado a biblioteca PaddleOCR v3.3.3 e PaddlePaddle v3.2.0.
O modelo de visão computacional usado é o **PP-OCRv5_server**. O modelo se saiu muito 
bem nos testes, principalmente quando a resolução da imagem era pequena, como 320x240p.
```bash
pip install requests
pip install pillow
python312 -m pip install paddlepaddle==3.2.0 paddleocr==3.3.3
```	 
A captura da imagem das placas se deu com a placa ESP32-S3-CAM Wroom em conjunto com a
câmera OV5640 de 5MP. Foi utilizado o CameraWebServer da própria biblioteca **'ESP32 by** 
**Espressif System'** do Arduino IDE para fazer as capturas. 

![Tela do sistema 5](interface_da_aplicacao/img5.png)
 

 ## CONFIGURAÇÕES COMPLEMENTARES:
```bash
pip install --upgrade PySide6 pyqtdarktheme"
```

 ## CRIAÇÃO DO EXECUTÁVEL PYTHON:
```bash
pip install pyinstaller

pyinstaller --onefile --windowed --clean ^
    --icon=icone.ico ^
    --version-file version_info.txt ^
    --add-data "imagens;imagens" ^
    SEIAParkingManagement.py
```

 ### Caso dê problemas de conflito entre PyQt5 e PySide6 com o erro "ERROR: Aborting build process due to attempt to collect multiple Qt bindings packages: attempting to run hook for 'PyQt5', while hook for 'PySide6' has already been run!". Execute o comando: 
```bash
pyinstaller --onefile --windowed --clean ^
    --icon=icone.ico ^
    --version-file version_info.txt ^
    --add-data "imagens;imagens" ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt5.QtCore ^
    --exclude-module PyQt5.QtGui ^
    --exclude-module PyQt5.QtWidgets ^
    SEIAParkingManagement.py
```



