create database seia_parking;
use seia_parking;

create table if not exists Autarquia(
    nome CHAR(16) PRIMARY KEY
);

create table if not exists Vaga(
    num_vaga INT PRIMARY KEY,
    autarquia CHAR(16) not null,
    foreign key (autarquia) references Autarquia(nome) on delete cascade
);

create table if not exists Carro(
    placa CHAR(8) PRIMARY KEY,
    num_vaga INT not null,
    autarquia CHAR(16) not null,
    modelo CHAR(100) not null,
    setor CHAR(200) not null,
    proprietario CHAR(200), -- ideal seria essa coluna referenciar Servidor(nome) - mas como não tenho os dados dos servidores como CPF, isso fica para outro momento.
    foreign key (num_vaga) references Vaga(num_vaga) on delete cascade,
    foreign key (autarquia) references Autarquia(nome) on delete cascade
);


create table if not exists Servidor(
    cpf_cnpj CHAR(14) PRIMARY KEY,
    nome CHAR(100) not null,
    autarquia CHAR(16) not null,
    foreign key (autarquia) references Autarquia(nome) on delete cascade
);

create table if not exists Registro(
    id INT AUTO_INCREMENT PRIMARY KEY,
    placa CHAR(8),
    cpf_cnpj CHAR(14),
    num_vaga INT not null,
    data_entrada DATETIME,
    data_saida DATETIME,
    tipo CHAR(10) not null,
    nome_visitante CHAR(100),
    foreign key (placa) references Carro(placa) on delete cascade,
    foreign key (cpf_cnpj) references Servidor(cpf_cnpj) on delete cascade,
    foreign key (num_vaga) references Vaga(num_vaga) on delete cascade
);

-- [ORDEM DE INSERÇÃO]
-- autarquia.sql
-- vagas.sql
-- servidor.sql (caso tenha os dados dos servidores de antemão)
-- carros.sql

source C:\SEIA\diretoria_inovacao\SEIAParkingManagement\database\autarquia.sql
source C:\SEIA\diretoria_inovacao\SEIAParkingManagement\database\vagas.sql
source C:\SEIA\diretoria_inovacao\SEIAParkingManagement\database\carros.sql

--SELECT * FROM carro c WHERE c.autarquia = 'seia' AND c.placa NOT IN (SELECT r.placa FROM registro r WHERE r.tipo = 'SAIDA');