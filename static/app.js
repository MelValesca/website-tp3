function validateTitre(titre, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);

  if (titre.length === 0 || titre.length > 50) {
    errorMessage.textContent =
      "Le titre doit contenir entre 1 et 50 caractères.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function validateDatePublication(datePublication) {
  var errorMessage = document.getElementById("error-date");

  if (!isValidDate(datePublication)) {
    errorMessage.textContent = "Date de publication invalide.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function validateContenu(contenu, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);

  if (contenu.length === 0 || contenu.length > 500) {
    errorMessage.textContent =
      "Le contenu doit contenir entre 1 et 500 caractères.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function isValidDate(dateString) {
  var regexDate = /^\d{4}-\d{2}-\d{2}$/;
  return regexDate.test(dateString);
}

function submitArticleForm(event) {
  var form = document.getElementById("article-form");
  var titre = form.querySelector('[name="titre"]').value;
  var datePublication = form.querySelector('[name="date_publication"]').value;
  var contenu = form.querySelector('[name="contenu"]').value;

  var titreValid = validateTitre(titre, "error-titre");
  var datePublicationValid = validateDatePublication(datePublication);
  var contenuValid = validateContenu(contenu, "error-contenu");

  if (!titreValid || !datePublicationValid || !contenuValid) {
    event.preventDefault();
  }
}

function submitModifierForm(event) {
  var form = document.getElementById("modifier-article");
  var titre = form.querySelector('[name="titre"]').value;
  var contenu = form.querySelector('[name="contenu"]').value;

  var titreValid = validateTitre(titre, "error-titre-modifier");
  var contenuValid = validateContenu(contenu, "error-contenu-modifier");
  if (!titreValid || !contenuValid) {
    event.preventDefault();
  }
}

function submitRechercheForm(event) {
  var inputValue = document.getElementById("recherche").value;
  var errorMessage = document.getElementById("error-message");

  if (inputValue.length < 3) {
    event.preventDefault();
    errorMessage.textContent =
      "La recherche doit contenir au moins 3 caractères.";
  } else {
    errorMessage.textContent = "";
  }
}

function submitNewUser(event) {
  event.preventDefault();
  var form = document.getElementById("creer-utilisateur");
  var username = form.querySelector('[name="username"]').value;
  var password = form.querySelector('[name="password"]').value;
  var prenom = form.querySelector('[name="prenom"]').value;
  var nom = form.querySelector('[name="nom"]').value;
  var courriel = form.querySelector('[name="courriel"]').value;
  var photo = getFileName("creer-utilisateur");

  var usernameValid = validateUsername(username, "error-username");
  var passwordValid = validatePassword(password, "error-password");
  var prenomValid = validatePrenom(prenom, "error-prenom");
  var nomValid = validateNom(nom, "error-nom");
  var courrielValid = validateCourriel(courriel, "error-courriel");
  var photoValid = validatePhoto(photo, "error-photo");

  if (
    usernameValid &&
    passwordValid &&
    prenomValid &&
    nomValid &&
    courrielValid &&
    photoValid
  ) {
    form.submit();
  }
}

function submitModifierUser(event) {
  event.preventDefault();
  var form = document.getElementById("modify-user");
  var password = form.querySelector('[name="password"]').value;
  var prenom = form.querySelector('[name="prenom"]').value;
  var nom = form.querySelector('[name="nom"]').value;
  var courriel = form.querySelector('[name="courriel"]').value;
  var photo = getFileName("modify-user");

  var passwordValid = validatePassword(password, "error-password-modifier");
  var prenomValid = validatePrenom(prenom, "error-prenom-modifier");
  var nomValid = validateNom(nom, "error-nom-modifier");
  var courrielValid = validateCourriel(courriel, "error-courriel-modifier");
  var photoValid = validatePhoto(photo, "error-photo-modifier");

  if (passwordValid && prenomValid && nomValid && courrielValid && photoValid) {
    form.submit();
  }
}

function getFileName(id) {
  var form = document.getElementById(id);
  var input = form.querySelector('[name="photo"]');
  if (input.files.length > 0) {
    var fileName = input.files[0].name;
    return fileName;
  }
  return null;
}

function validateUsername(username, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);

  if (!username || username.length > 25 || username.length < 3) {
    errorMessage.textContent =
      "Le username doit contenir entre 3 et 25 caractères.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function validatePassword(password, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);
  if (!password || password.length > 25 || password.length < 3) {
    errorMessage.textContent =
      "Le password doit contenir entre 3 et 25 caractères.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function validateNom(nom, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);
  if (!nom || nom.length > 20 || nom.length < 3) {
    errorMessage.textContent = "Le nom doit contenir entre 3 et 20 caractères.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function validatePrenom(prenom, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);
  if (!prenom || prenom.length > 20 || prenom.length < 3) {
    errorMessage.textContent =
      "Le prenom doit contenir entre 3 et 20 caractères.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function validateCourriel(courriel, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);
  if (!courriel || courriel.length > 100) {
    errorMessage.textContent =
      "Le courriel doit avoir moins de 100 caractères.";
    return false;
  } else if (!/[^@]+@[^@]+\.[^@]+/.test(courriel)) {
    errorMessage.textContent =
      "Le courriel doit avoir le format exemple@hotmail.com.";
    return false;
  } else {
    errorMessage.textContent = "";
    return true;
  }
}

function validatePhoto(image, erreur_msg) {
  var errorMessage = document.getElementById(erreur_msg);
  if (!image || (image && image.toLowerCase().endsWith(".png"))) {
    errorMessage.textContent = "";
    return true;
  } else {
    errorMessage.textContent =
      "La photo de profile doit être une image png valide.";
    return false;
  }
}

function isValidDate(dateStr) {
  var datePattern = /^\d{4}-\d{2}-\d{2}$/;
  return datePattern.test(dateStr);
}

document.addEventListener("DOMContentLoaded", function () {
  var currentPage = window.location.pathname.substring(1);
  var currentLink = document.getElementById(currentPage);

  if (currentLink) {
    currentLink.classList.add("bouton-menu-apres");
    currentLink.classList.remove("bouton-menu");
  }

  var articleForm = document.getElementById("article-form");
  if (articleForm) {
    articleForm.addEventListener("submit", submitArticleForm);
  }

  var modifierForm = document.getElementById("modifier-article");
  if (modifierForm) {
    modifierForm.addEventListener("submit", submitModifierForm);
  }

  var ajouterUser = document.getElementById("creer-utilisateur");
  if (ajouterUser) {
    ajouterUser.addEventListener("submit", submitNewUser);
  }

  var modifierUser = document.getElementById("modify-user");
  if (modifierUser) {
    modifierUser.addEventListener("submit", submitModifierUser);
  }

  var rechercheForm = document.getElementById("recherche-id");
  if (rechercheForm) {
    rechercheForm.addEventListener("submit", submitRechercheForm);
  }
});
