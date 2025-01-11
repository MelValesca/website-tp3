## Utilisation

Avant de commencer, assurez-vous d'avoir Python et Flask installés sur votre système. Voici les étapes à suivre pour exécuter le projet :

1. (Recommandé) Créez un environnement virtuel pour isoler les dépendances du projet. Vous pouvez utiliser virtualenv ou venv. Voici comment créer un environnement virtuel avec venv :

```sh
python3 -m venv env
```

2. Activez l'environnement virtuel :

* Sous Windows : `env\Scripts\activate`
* Sous MacOS, Linux : `source env/bin/activate`

3. Installez les dépendances :


```sh
pip3 install -r requirements.txt
```

4. Démarrez le serveur avec la commande make :

```sh
make
```

Le serveur devrait être opérationnel et accessible à l'adresse http://localhost:5000.

5. Pour arrêter le serveur, appuyez sur Ctrl+C dans le terminal.

N'oubliez pas de désactiver l'environnement virtuel lorsque vous avez terminé avec la commande :

```sh
deactivate
```

## Technologies utilisées

Ce projet utilise les technologies suivantes :

* Python : Le langage de programmation principal utilisé pour écrire les scripts backend.
* Flask : Un micro-framework pour Python utilisé pour développer des applications web.
* HTML : Utilisé pour structurer les pages web.
* CSS : Utilisé pour styliser les pages web.
* JavaScript : Utilisé pour ajouter des fonctionnalités interactives sur les pages web.
* Jinja : Un moteur de template utilisé pour générer du HTML dynamique à partir des modèles.
* SQL : Langage utilisé pour gérer la base de données et effectuer des requêtes.
* Make : Utilisé pour automatiser les tâches de build et de déploiement.


