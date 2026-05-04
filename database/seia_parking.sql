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
    placa CHAR(8) not null,
    cpf_cnpj CHAR(14) not null,
    num_vaga INT not null,
    data_saida DATETIME,
    data_entrada DATETIME,
    tipo CHAR(10) not null,
    foreign key (placa) references Carro(placa) on delete cascade,
    foreign key (cpf_cnpj) references Servidor(cpf_cnpj) on delete cascade,
    foreign key (num_vaga) references Vaga(num_vaga) on delete cascade
);

source C:\Users\pablo.resi\Documents\Diretoria Inovacao\blank project\pyside6\database\autarquia.sql
source C:\Users\pablo.resi\Documents\Diretoria Inovacao\blank project\pyside6\database\vagas.sql
source C:\Users\pablo.resi\Documents\Diretoria Inovacao\blank project\pyside6\database\carros.sql

--SELECT * FROM carro c WHERE c.autarquia = 'seia' AND c.placa NOT IN (SELECT r.placa FROM registro r WHERE r.tipo = 'SAIDA');