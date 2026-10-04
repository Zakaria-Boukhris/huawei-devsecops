# Gestion du matériel et pipeline DevSecOps

Ce dépôt réunit une application Django de gestion du matériel et un workflow GitHub Actions qui vérifie son code, sa configuration et son image Docker avant publication. Projet réalisé par **Zakaria Boukhris et Walid Salhi**.

## Application Django

L’application sépare les parcours employés et administrateurs : consultation des matériels, création et suivi des demandes, gestion des équipements et traitement des demandes. Les modules `users/`, `materiel/` et `demandes/` contiennent les modèles et les vues ; `templates/` contient les pages HTML. La configuration fournie utilise SQLite pour le développement.

### Lancer en local

Prérequis : Python 3.12 ou version compatible avec les dépendances du projet.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
DEBUG=True SECRET_KEY=cle-locale-a-remplacer python manage.py runserver
```

Sous Windows, activer l’environnement avec `.venv\Scripts\activate` et définir les variables d’environnement selon le terminal utilisé. Les comptes et données de démonstration doivent être créés localement ; `db.sqlite3` n’est pas versionné.

## Pipeline de sécurité

Le workflow [`.github/workflows/ci-security.yml`](.github/workflows/ci-security.yml) se déclenche sur les changements de la branche `main` et les pull requests :

| Étape | Outil | Comportement configuré |
| --- | --- | --- |
| Recherche de secrets | Gitleaks | Bloque le workflow en cas de détection. |
| Analyse statique Python | Semgrep et Bandit | Bloque selon les seuils configurés. |
| Audit du Dockerfile et des manifestes | Checkov | Rapport non bloquant (`--soft-fail`). |
| Construction et scan de l’image | Docker et Trivy | Bloque sur les vulnérabilités HIGH ou CRITICAL non corrigées. |
| Publication | GHCR | Pousse les images associées au commit et à `latest` après les contrôles. |

Le dossier `k8s/` fournit un déploiement, un service et un namespace ; `policies/` fournit deux politiques Kyverno. **Le workflow ne réalise pas de déploiement Kubernetes.** Les manifestes sont des exemples à adapter : ils attendent un secret `django-secrets`, utilisent une image `latest` à épingler pour une mise en production et une base SQLite locale n’est pas adaptée telle quelle à deux réplicas avec un système de fichiers en lecture seule.

## Organisation

```text
.github/workflows/    Pipeline GitHub Actions
users/                Authentification et comptes
materiel/             Équipements
demandes/             Demandes
templates/            Interfaces HTML
k8s/                  Manifestes Kubernetes
policies/             Politiques Kyverno
```

Ce dépôt décrit le code et la configuration présents. Les résultats des outils de sécurité et un déploiement en production doivent être vérifiés sur l’onglet Actions et dans l’environnement cible.
