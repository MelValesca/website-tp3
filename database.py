import sqlite3
from datetime import date
import hashlib
import secrets


def _build_article(data):
    article = {
        "id": data[0],
        "titre": data[1],
        "auteur": data[2],
        "date_publication": data[3],
        "contenu": data[4],
    }
    return article


def _build_user(data):
    user = {
        "id": data[0],
        "username": data[1],
        "password_hash": data[2],
        "salt": data[3],
        "nom": data[4],
        "prenom": data[5],
        "courriel": data[6],
        "actif": data[7],
        "pic_id": data[8],
    }
    return user


def hash_password(password, salt):
    hash_object = hashlib.sha512(str(password + salt).encode("utf-8"))
    return hash_object.hexdigest()


def generate_salt(length=16):
    salt_bytes = secrets.token_bytes(length)
    return salt_bytes.hex()


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect("db/database.db")
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_articles(self):
        cursor = self.get_connection().cursor()
        query = (
            "SELECT id, titre, identifiant, auteur, "
            "date_publication, contenu "
            "FROM Articles"
        )
        cursor.execute(query)
        all_data = cursor.fetchall()
        articles = [_build_article(item) for item in all_data]
        cursor.close()
        return articles

    def get_article(self, article_id):
        cursor = self.get_connection().cursor()
        query = (
            "SELECT id, titre, auteur, date_publication, contenu "
            "FROM Articles WHERE id = ?"
        )
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()
        cursor.close()
        if article is None:
            return None
        else:
            return _build_article(article)

    def get_articles_ordered_by_date(self):
        connection = self.get_connection()
        cursor = connection.cursor()

        query = (
            "SELECT id, titre, auteur, date_publication, contenu "
            "FROM Articles "
            "ORDER BY date_publication DESC"
        )
        cursor.execute(query)
        articles_data = cursor.fetchall()

        cursor.close()

        articles = [
            _build_article(article_data)
            for article_data in articles_data
        ]

        return articles

    def get_derniers_articles(self):
        connection = self.get_connection()
        cursor = connection.cursor()

        today_date = date.today()

        query = (
            "SELECT id, titre, auteur, date_publication, contenu "
            "FROM Articles "
            "WHERE date_publication <= ? "
            "ORDER BY date_publication DESC "
            "LIMIT 5"
        )
        cursor.execute(query, (today_date,))
        articles_data = cursor.fetchall()

        cursor.close()

        articles = [
            _build_article(article_data)
            for article_data in articles_data
        ]

        return articles

    def search_articles(self, search_query):
        connection = self.get_connection()
        cursor = connection.cursor()
        today_date = date.today()

        query = (
            "SELECT id, titre, auteur, date_publication, contenu "
            "FROM Articles "
            "WHERE (titre LIKE ? OR contenu LIKE ?) AND date_publication <= ? "
            "ORDER BY date_publication DESC "
            "LIMIT 5"
        )
        cursor.execute(
            query, (
                "%" + search_query + "%", "%"
                + search_query + "%", today_date
            )
        )
        articles_data = cursor.fetchall()

        cursor.close()

        articles = [
            _build_article(article_data)
            for article_data in articles_data
        ]

        return articles

    def add_article(self, titre, auteur, date_publication, contenu):
        connection = self.get_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Articles")
        cursor.close()

        identifiant = titre.replace(" ", "-")

        query = (
            "INSERT INTO Articles"
            "(id,titre, auteur, date_publication, contenu) "
            "VALUES(?, ?, ?, ?, ?)"
        )
        connection.execute(
            query, (identifiant, titre, auteur, date_publication, contenu)
        )
        connection.commit()

        return identifiant

    def modify_article(self, id, titre, contenu):
        connection = self.get_connection()

        query = "UPDATE Articles " "SET titre = ?, contenu = ? " "WHERE id = ?"

        connection.execute(query, (titre, contenu, id))
        connection.commit()

        return id

    def create_user(self, username, password, prenom, nom, courriel, pic_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Utilisateurs")

        id = cursor.fetchone()[0] + 1
        salt = generate_salt()
        password = hash_password(password, salt)

        connection.execute(
            (
                "insert into Utilisateurs"
                "(id,username, password_hash, salt,"
                "prenom, nom, courriel, pic_id)"
                " values(?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            (id, username, password, salt, prenom, nom, courriel, pic_id),
        )
        connection.commit()
        connection.close()

    def create_picture(self, pic_id, file_data):
        connection = self.get_connection()
        file_data.seek(0)
        file_content = file_data.read()
        connection.execute(
            "insert into ProfilPhotos(pic_id, photo_profil) values(?, ?)",
            (pic_id, file_content),
        )
        connection.commit()

    def modify_picture(self, pic_id, photo):
        connection = self.get_connection()
        photo.seek(0)
        photo_data = photo.read()
        query = (
            "UPDATE ProfilPhotos "
            "SET photo_profil = ? "
            "WHERE pic_id = ?"
        )

        connection.execute(query, (photo_data, pic_id))
        connection.commit()

    def load_picture(self, pic_id):
        cursor = self.get_connection().cursor()
        cursor.execute(
            ("select photo_profil from ProfilPhotos where pic_id=?"), (pic_id,)
        )
        picture = cursor.fetchone()
        if picture is None:
            return None
        else:
            blob_data = picture[0]
            return blob_data

    def get_photo(self, nom_prenom):
        prenom, nom = nom_prenom.split()
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT pic_id FROM Utilisateurs WHERE nom = ? AND prenom = ?",
            (nom, prenom),
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def validate_user(self, username, password):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT password_hash, salt, actif "
            "FROM Utilisateurs WHERE username = ?",
            (username,),
        )
        user_record = cursor.fetchone()

        if user_record:
            stored_password_hash, salt, actif = user_record
            hashed_password = hash_password(password, salt)

            if hashed_password == stored_password_hash and actif:
                return True
            else:
                return False
        else:
            return False

    def get_user_fullname(self, username):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT prenom,nom FROM Utilisateurs WHERE username = ?",
            (username,)
        )
        user_data = cursor.fetchone()

        if user_data is None:
            return None

        prenom, nom = user_data
        return f"{prenom} {nom}"

    def get_user(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Utilisateurs WHERE id = ?", (id,))
        user_data = cursor.fetchone()

        if not user_data:
            return None

        return _build_user(user_data)

    def get_user_status(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT actif FROM Utilisateurs WHERE id = ?", (id,))
        return cursor.fetchone()[0]

    def modify_user_status(self, id):
        connection = self.get_connection()
        actif = self.get_user_status(id)
        query = "UPDATE Utilisateurs " "SET actif = ? " "WHERE id = ?"

        connection.execute(query, (not actif, id))
        connection.commit()

    def get_password(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT password_hash,salt FROM Utilisateurs WHERE id = ?", (id,)
        )
        password_data = cursor.fetchone()

        if password_data:
            password_hash, salt = password_data
            return password_hash, salt
        else:
            return None

    def get_all_users(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Utilisateurs")
        users_data = cursor.fetchall()

        if not users_data:
            return None

        users = [_build_user(user_data) for user_data in users_data]

        return users

    def modify_user(self, id, password, prenom, nom, courriel, pic_id):
        connection = self.get_connection()
        if not password:
            password_hash, salt = self.get_password(id)
        else:
            salt = generate_salt()
            password_hash = hash_password(password, salt)

        query = (
            "UPDATE Utilisateurs "
            "SET password_hash = ?, salt = ?, prenom = ?,"
            "nom = ?, courriel = ?, pic_id = ? "
            "WHERE id = ?"
        )

        connection.execute(
            query, (password_hash, salt, prenom, nom, courriel, pic_id, id)
        )
        connection.commit()

    def is_username_taken(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute(
            ("SELECT COUNT(*) FROM Utilisateurs where username = ?"),
            (username,)
        )
        data = cursor.fetchone()[0]
        return data > 0

    def save_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(
            ("insert into sessions(id_session, utilisateur) " "values(?, ?)"),
            (id_session, username),
        )
        connection.commit()

    def delete_session(self, id_session):
        connection = self.get_connection()
        connection.execute(
            ("delete from sessions where id_session=?"),
            (id_session,)
        )
        connection.commit()

    def get_session(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute(
            ("select utilisateur from sessions where id_session=?"),
            (id_session,)
        )
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def is_session_active(self, id_session):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sessions WHERE id_session = ?", (id_session,)
        )
        count = cursor.fetchone()[0]
        return count > 0
