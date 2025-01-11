from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    Response,
    make_response,
)
from .database import Database
from flask import g
from functools import wraps
import uuid
import re

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = "(*&*&322387he738220)(*(*22347657"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.disconnect()


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return render_template("login.html")
        else:
            return f(*args, **kwargs)

    return decorated


def is_authenticated(session):
    if "id" in session:
        id_session = session["id"]
        return get_db().is_session_active(id_session)
    return False


@app.route("/")
def main():
    db = get_db()
    derniers_articles = db.get_derniers_articles()
    return render_template("index.html", derniers_articles=derniers_articles)


@app.route("/recherche", methods=["POST"])
def recherche():
    if request.method == "POST":
        recherche = request.form["recherche"]
        if valider_recherche(recherche) is not None:
            return render_template(
                "index.html",
                derniers_articles=get_db().get_derniers_articles(),
                erreur=valider_recherche(recherche),
            )
        db = get_db()
        articles = db.search_articles(recherche)
        return render_template(
            "recherche.html",
            articles=articles,
            nb_item=len(articles),
            recherche=recherche,
        )


@app.route("/admin-nouveau")
@authentication_required
def ajouter():
    erreurs = {}
    valeurs = {}
    return render_template(
        "admin-nouveau.html", erreurs=erreurs, valeurs=valeurs
    )


@app.route("/submit_article", methods=["POST"])
@authentication_required
def submit_article():
    valeurs = {}
    if request.method == "POST":
        valeurs["titre"] = request.form["titre"]
        valeurs["date_publication"] = request.form["date_publication"]
        valeurs["contenu"] = request.form["contenu"]

        erreurs = valider_article(
            valeurs["titre"], valeurs["date_publication"], valeurs["contenu"]
        )
        if erreurs:
            return render_template(
                "admin-nouveau.html", erreurs=erreurs, valeurs=valeurs
            )

        db = get_db()
        username = db.get_session(session["id"])
        auteur = db.get_user_fullname(username)
        article_id = db.add_article(
            valeurs["titre"], auteur, valeurs["date_publication"],
            valeurs["contenu"]
        )
        return redirect(f"/article/{article_id}")


@app.route("/article/<identifiant>", methods=["GET"])
def article(identifiant):
    db = get_db()
    article = db.get_article(identifiant)
    if article is None:
        return render_template("404.html"), 404
    pic_id = db.get_photo(article["auteur"])
    return render_template("article.html", article=article, pic_id=pic_id)


@app.route("/modifier-article/<identifiant>", methods=["GET", "POST"])
@authentication_required
def modify_item(identifiant):
    db = get_db()
    erreurs = {}
    valeurs = {}
    article = db.get_article(identifiant)
    if article is None:
        return render_template("404.html"), 404
    valeurs["titre"] = article["titre"]
    valeurs["contenu"] = article["contenu"]
    if request.method == "POST":
        valeurs["titre"] = request.form["titre"]
        valeurs["contenu"] = request.form["contenu"]
        erreurs = valider_modification_article(
            valeurs["titre"], valeurs["contenu"]
        )
        if not erreurs:
            db.modify_article(
                identifiant, valeurs["titre"], valeurs["contenu"]
            )
            return redirect(f"/article/{identifiant}")

    return render_template(
        "modifier-article.html", article=article,
        erreurs=erreurs, valeurs=valeurs
    )


@app.route("/admin")
@authentication_required
def admin():
    db = get_db()
    return render_template(
        "admin-articles.html", articles=db.get_articles_ordered_by_date()
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    if db.validate_user(username, password):
        id_session = uuid.uuid4().hex
        db.save_session(id_session, username)
        session["id"] = id_session
        return redirect("/admin")
    else:
        return render_template(
            "login.html", message="Mauvais username/password."
        )


@app.route("/image/<pic_id>.png")
def download_picture(pic_id):
    db = get_db()
    binary_data = db.load_picture(pic_id)
    if binary_data is None:
        return Response(status=404)
    else:
        response = make_response(binary_data)
        response.headers.set("Content-Type", "image/png")
    return response


@app.route("/utilisateurs")
@authentication_required
def utilisateurs():
    db = get_db()
    utilisateurs = db.get_all_users()
    return render_template("utilisateurs.html", utilisateurs=utilisateurs)


@app.route("/ajouter-utilisateur", methods=["GET", "POST"])
@authentication_required
def ajouter_utilisateur():
    valeurs = {}
    erreurs = {}
    if request.method == "GET":
        return render_template(
            "ajouter-utilisateur.html", valeurs=valeurs, erreurs=erreurs
        )
    else:
        valeurs["username"] = request.form["username"]
        valeurs["password"] = request.form["password"]
        valeurs["prenom"] = request.form["prenom"]
        valeurs["nom"] = request.form["nom"]
        valeurs["courriel"] = request.form["courriel"]
        photo = None
        valeurs["picture_id"] = None
        if "photo" in request.files and request.files["photo"].filename:
            photo = request.files["photo"]
            valeurs["picture_id"] = str(uuid.uuid4().hex)

        erreurs = valider_user(
            valeurs["username"],
            valeurs["password"],
            valeurs["prenom"],
            valeurs["nom"],
            valeurs["courriel"],
            photo,
        )
        if len(erreurs) == 0:
            db = get_db()

            if valeurs["picture_id"] is not None:
                db.create_picture(valeurs["picture_id"], photo)
            db.create_user(
                valeurs["username"],
                valeurs["password"],
                valeurs["prenom"],
                valeurs["nom"],
                valeurs["courriel"],
                valeurs["picture_id"],
            )
            return redirect(url_for("utilisateurs"))
        else:
            return render_template(
                "ajouter-utilisateur.html", valeurs=valeurs, erreurs=erreurs
            )


@app.route("/modifier-utilisateur/<identifiant>", methods=["GET", "POST"])
@authentication_required
def modifier_utilisateur(identifiant):
    db = get_db()
    valeurs = {}
    erreurs = {}
    utilisateur = db.get_user(identifiant)
    if utilisateur is None:
        return render_template("404.html"), 404
    if request.method == "GET":
        valeurs["username"] = utilisateur["username"]
        valeurs["prenom"] = utilisateur["prenom"]
        valeurs["nom"] = utilisateur["nom"]
        valeurs["courriel"] = utilisateur["courriel"]
        return render_template(
            "modifier-utilisateur.html",
            user=utilisateur,
            valeurs=valeurs,
            erreurs=erreurs,
        )
    else:
        valeurs["password"] = request.form["password"]
        valeurs["prenom"] = request.form["prenom"]
        valeurs["nom"] = request.form["nom"]
        valeurs["courriel"] = request.form["courriel"]
        photo = None

        db = get_db()
        if "photo" in request.files and request.files["photo"].filename:
            photo = request.files["photo"]
            if is_png_image_valide(photo):
                if utilisateur["pic_id"] is None:
                    utilisateur["pic_id"] = str(uuid.uuid4().hex)
                    db.create_picture(utilisateur["pic_id"], photo)
                else:
                    db.modify_picture(utilisateur["pic_id"], photo)

        erreurs = valider_user_modifier(
            valeurs["password"],
            valeurs["prenom"],
            valeurs["nom"],
            valeurs["courriel"],
            photo,
        )
        if len(erreurs) == 0:
            db.modify_user(
                identifiant,
                valeurs["password"],
                valeurs["prenom"],
                valeurs["nom"],
                valeurs["courriel"],
                utilisateur["pic_id"],
            )
            return redirect(url_for("utilisateurs"))
        else:
            return render_template(
                "modifier-utilisateur.html",
                user=utilisateur,
                valeurs=valeurs,
                erreurs=erreurs,
            )


@app.route("/modifier-statut/<identifiant>", methods=["POST"])
@authentication_required
def modifier_statut(identifiant):
    db = get_db()
    utilisateur = db.get_user(identifiant)
    if utilisateur is None:
        return render_template("404.html"), 404
    else:
        db.modify_user_status(identifiant)
        return redirect(url_for("utilisateurs"))


@app.route("/logout")
@authentication_required
def logout():
    id_session = session["id"]
    session.pop("id", None)
    get_db().delete_session(id_session)
    return redirect("/")


@app.errorhandler(404)
def page_not_found(erreur):
    return render_template("404.html"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template("405.html"), 405


def valider_recherche(recherche):
    if len(recherche) < 3:
        return "La recherche doit contenir au moins 3 caractères."


def valider_article(titre, date_publication, contenu):
    erreurs = {}

    if not titre or len(titre) > 50:
        erreurs["titre"] = "Le titre doit contenir entre 1 et 50 caractères."

    if not is_valid_date(date_publication):
        erreurs["date_publication"] = "Date de publication invalide."

    if not contenu or len(contenu) > 500:
        erreurs["contenu"] = "Le contenu doit contenir de 1 à 500 caractères."

    return erreurs


def valider_modification_article(titre, contenu):
    erreurs = {}

    if not titre or len(titre) > 50:
        erreurs["titre"] = "Le titre doit contenir entre 1 et 50 caractères."

    if not contenu or len(contenu) > 500:
        erreurs["contenu"] = "Le contenu doit contenir de 1 à 500 caractères."

    return erreurs


def valider_user(username, password, prenom, nom, courriel, photo):
    erreurs = {}
    if valider_username(username) is not None:
        erreurs["username"] = valider_username(username)

    if not password or len(password) > 25 or len(password) < 3:
        erreurs["password"] = "Le password doit contenir de 3 à 25 caractères."

    if not nom or len(nom) > 20 or len(nom) < 3:
        erreurs["nom"] = "Le nom doit contenir entre 3 et 20 caractères."

    if not prenom or len(prenom) > 20 or len(prenom) < 3:
        erreurs["prenom"] = "Le prenom doit contenir de 3 à 20 caractères."

    if not is_png_image_valide(photo):
        erreurs["photo"] = "La photo de profil doit être une image png valide."

    if is_courriel_valide(courriel) is not None:
        erreurs["courriel"] = is_courriel_valide(courriel)

    return erreurs


def valider_user_modifier(password, prenom, nom, courriel, photo):
    erreurs = {}

    if not password or len(password) > 25 or len(password) < 3:
        erreurs["password"] = "Le password doit contenir de 3 à 25 caractères."

    if not nom or len(nom) > 20 or len(nom) < 3:
        erreurs["nom"] = "Le nom doit contenir entre 3 et 20 caractères."

    if not prenom or len(prenom) > 20 or len(prenom) < 3:
        erreurs["prenom"] = "Le prenom doit contenir de 3 à 20 caractères."

    if not is_png_image_valide(photo):
        erreurs["photo"] = "La photo de profil doit être une image png valide."

    if is_courriel_valide(courriel) is not None:
        erreurs["courriel"] = is_courriel_valide(courriel)

    return erreurs


def valider_username(username):
    db = get_db()
    if not username or len(username) > 25 or len(username) < 3:
        return "Le username doit contenir entre 3 et 25 caractères."
    elif db.is_username_taken(username):
        return "Ce nom d'utilisateur existe déjà"


def is_courriel_valide(courriel):
    if not courriel or len(courriel) > 100:
        return "Le courriel doit avoir moins de 100 caractères."
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", courriel):
        return "Le courriel doit avoir le format exemple@hotmail.com."


def is_png_image_valide(image):
    if not image or image.read() == b"":
        return True
    else:
        png_signature = b"\x89PNG\r\n\x1a\n"
        image.seek(0)
        file_signature = image.read(8)
        return file_signature == png_signature


def is_valid_date(date_str):
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"

    if re.search(date_pattern, date_str):
        return True
    else:
        return False
