CREATE TABLE Articles (
    id varchar(50) PRIMARY KEY NOT NULL,
    titre varchar(50) NOT NULL,
    auteur varchar(40) NOT NULL,
    date_publication DATE NOT NULL,
    contenu varchar(500) NOT NULL
);
CREATE TABLE sessions (
  id integer primary key UNIQUE NOT NULL,
  id_session varchar(32) UNIQUE NOT NULL,
  utilisateur varchar(25) NOT NULL
);
CREATE TABLE Utilisateurs (
    id INTEGER PRIMARY KEY,
    username VARCHAR(25) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    nom VARCHAR(20) NOT NULL,
    prenom VARCHAR(20) NOT NULL,
    courriel VARCHAR(100) NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    pic_id VARCHAR(32));
CREATE TABLE ProfilPhotos (
    pic_id VARCHAR(32) PRIMARY KEY,
    photo_profil BLOB NOT NULL
);
