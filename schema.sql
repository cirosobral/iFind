CREATE TABLE noticias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    autor TEXT not null,
    content TEXT NOT NULL,
    url TEXT not null,
    fonte TEXT not null
);

CREATE TABLE mapas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL
);

CREATE TABLE setores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_mapa TEXT NOT NULL,
    title TEXT NOT NULL,
    descricao TEXT NOT NULL,
    url TEXT NOT NULL,
    x text not null default '0',
    y text not null default '0'
);

CREATE TABLE eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    autor TEXT not null,
  
    data TEXT NOT NULL,
    descricao TEXT not null,
    local TEXT not null
  );

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL,
    authenticated BOOLEAN DEFAULT(FALSE)
);

CREATE TABLE cronogramas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT NOT NULL,
    turma TEXT NOT NULL
);

CREATE TABLE horarios (
    id_cronograma INTEGER,
    horario INTEGER,
    dia TEXT,
    disciplina TEXT,
    professor TEXT,
    PRIMARY KEY(id_cronograma, horario, dia)
);