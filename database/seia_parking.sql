create database seia_parking;
use seia_parking;

create table if not exists Autarquia(
    nome CHAR(16) PRIMARY KEY
);

create table if not exists Vaga(
    num_vaga INT PRIMARY KEY,
    autarquia CHAR(16),
    foreign key (autarquia) references Autarquia(nome) on delete cascade
);

create table if not exists Servidor(
    cpf_cnpj CHAR(14) PRIMARY KEY,
    nome CHAR(100) not null,
    autarquia CHAR(16) not null,
    foreign key (autarquia) references Autarquia(nome) on delete cascade
);

create table if not exists Carro(
    placa CHAR(8) PRIMARY KEY,
    num_vaga INT not null,
    autarquia CHAR(16) not null,
    modelo CHAR(100) not null,
    setor CHAR(200) not null,
    proprietario_cpf CHAR(14), 
    foreign key (num_vaga) references Vaga(num_vaga) on delete cascade,
    foreign key (autarquia) references Autarquia(nome) on delete cascade,
    foreign key (proprietario_cpf) references Servidor(cpf_cnpj) on delete set null
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
-- Autarquia
-- Vaga
-- Servidor
-- Carro
-- Registro

source C:\Users\Usuario\Documents\SEIAParkingManagement\database\autarquia.sql
source C:\Users\Usuario\Documents\SEIAParkingManagement\database\vagas.sql
-- ...

