Voici une structure de **README.md** professionnelle, rédigée en français pour refléter le contexte de votre cabinet au Gabon, et organisée pour un projet monorepo moderne.

---

### 📝 Fichier : `README.md` (à la racine de `ged_project`)

```markdown
# ⚖️ GED Cabinet - Gestion Électronique de Documents Juridiques

Ce projet est une solution complète de **Gestion Électronique de Documents (GED)** conçue spécifiquement pour les cabinets d'avocats. Elle permet de centraliser les dossiers clients, de gérer l'arborescence des pièces juridiques et d'assurer la conformité RGPD (loi gabonaise sur la protection des données).

## 🚀 Architecture du Projet (Monorepo)

Le projet est divisé en deux parties principales :
* **`/backend`** : API REST développée avec **Django 5.2** et **Django REST Framework**.
* **`/frontend`** : Interface utilisateur développée avec **Vue.js 3**, **Vuetify 3** et **Pinia**.

---

## 🛠️ Stack Technique

**Backend :**
* Python 3.12+ / Django 5.2
* Django REST Framework (DRF)
* Authentification : JWT (SimpleJWT)
* Base de données : SQLite (Développement) / PostgreSQL (Production cible)

**Frontend :**
* Vue.js 3 (Composition API)
* Vuetify 3 (UI Components)
* Pinia (Gestion d'état)
* Axios (Appels API)
* Vite (Build tool)

---

## ⚙️ Installation et Configuration

### 1. Prérequis
* Python installé
* Node.js (v18+) et npm installés
* Git installé

### 2. Configuration du Backend
```bash
cd backend
# Création de l'environnement virtuel
python -m venv venv
# Activation (Windows)
.\venv\Scripts\activate

# Installation des dépendances
pip install -r requirements.txt

# Migrations de la base de données
python manage.py migrate

# Lancement du serveur
python manage.py runserver

```

*Le backend sera accessible sur : `http://127.0.0.1:8000/api/*`

### 3. Configuration du Frontend

```bash
cd frontend
# Installation des dépendances
npm install

# Lancement en mode développement
npm run dev

```

*Le frontend sera accessible sur : `http://localhost:5173/*`

---

## 🔒 Fonctionnalités Clés

* **Gestion des Clients** : Distinction entre Personnes Physiques et Personnes Morales (NIF, RCCM).
* **Gestion des Dossiers** : Suivi des procédures, dates critiques et statuts.
* **Système de GED** :
* Arborescence de dossiers par affaire.
* Upload de documents avec gestion de la sensibilité (Normal, Confidentiel, Critique).
* Calcul automatique des hachages de fichiers pour l'intégrité.


* **Sécurité** : Authentification JWT et gestion des rôles (Avocats, Secrétariat, Administrateur).
* **Conformité** : Module de consentement RGPD intégré.

---

## 📁 Structure du Dossier

```text
ged_project/
├── backend/            # Code source Django
│   ├── apps/           # Modules métier (users, clients, dossiers, documents)
│   ├── config/         # Paramètres du projet
│   └── manage.py
├── frontend/           # Code source Vue.js
│   ├── src/
│   │   ├── components/ # Composants réutilisables
│   │   ├── views/      # Pages de l'application
│   │   ├── stores/     # État Pinia
│   │   └── plugins/    # Configuration Axios/Vuetify
│   └── package.json
└── README.md

```

---

## 👨‍💻 Auteur

* **SOUARE Ahmed** - *Développement & Architecture* - Cabinet de Libreville, Gabon.

---

© 2026 - Système de Gestion Juridique. Tous droits réservés.

```
