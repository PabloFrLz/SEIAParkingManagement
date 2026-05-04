/*
*  Project Parking Management v 1.0.0.01
*  Software de Controle de Estacionamento Institucional
*
*/

 * PREPARANDO O AMBIENTE:
	• winget install Python.Python.3.13
	• pip install pyside6
	• pip install pyqtdarktheme
	• pip install pymysql
	• pip install cryptography

 * CONFIGURANDO O BANCO:
	NOTA: instalar o mysql server 8.0 e setar as variaveis de ambiente se for necessário.
	• Modificar as variaveis globais USER e PASSWORD do arquivo SEIAParkingManagement.py com as credenciais do seu banco de dados;
 	• Entrar no banco via cmd e executar o codigo:
		source C:(caminho_para_projeto)\SEIAParkingManagement\database\seia_parking.sql
		source C:(caminho_para_projeto)\SEIAParkingManagement\database\autarquia.sql
		source C:(caminho_para_projeto)\SEIAParkingManagement\database\vagas.sql
		source C:(caminho_para_projeto)\SEIAParkingManagement\database\carros.sql
	 
 
 * CONFIGURAÇÕES FINAIS:
	-executar "pip install --upgrade PySide6 pyqtdarktheme"
	