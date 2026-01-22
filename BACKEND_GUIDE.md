**`BACKEND_GUIDE.md`** 
---

# 🏗️ Architecture Backend (Django REST)

L'application suit une architecture modulaire basée sur le principe de séparation des responsabilités. Le dossier `apps/` centralise toute la logique métier du cabinet.

## 📂 Structure des Modules (`/backend/apps/`)

Chaque application possède sa propre responsabilité et ses propres modèles de données.

| Module | Responsabilité | Modèles Clés |
| --- | --- | --- |
| **`users`** | Gestion des comptes et rôles | `User` (Custom User Model) |
| **`clients`** | Base de données des mandants | `Client` (Physique/Morale) |
| **`dossiers`** | Cœur métier : procédures et affaires | `Dossier` |
| **`documents`** | Système de GED et arborescence | `Folder`, `Document` |
| **`audit`** | Traçabilité et journalisation (RGPD) | `AuditLog` |
| **`agenda`** | Échéances et calendrier juridique | `Event` |

---

## 🔍 Focus sur les Modèles de Données

### 📂 Module `dossiers` (`apps/dossiers/models.py`)

Le modèle **`Dossier`** est le pivot du système.

* **Relations** : Lié à un `Client` (propriétaire) et à un `User` (avocat responsable).
* **Données** : Contient le code de référence unique, le titre de l'affaire, le tribunal/juridiction et les dates critiques.

### 📄 Module `documents` (`apps/documents/models.py`)

Ce module gère le stockage physique et logique des pièces.

* **`Folder`** : Gère l'arborescence récursive (un dossier peut contenir des sous-dossiers). Chaque dossier est obligatoirement rattaché à un `Dossier` juridique.
* **`Document`** :
* Gère le fichier physique via `FileField`.
* **Intégrité** : Stocke un `file_hash` (SHA-256) pour garantir que le document n'est pas modifié.
* **Confidentialité** : Utilise un champ `sensitivity` pour restreindre l'accès aux pièces critiques.
* **Versionnage** : Lié à lui-même via `previous_version` pour conserver l'historique des modifications.



---

## 🛠️ Organisation Interne d'une App Django

Pour chaque module (ex: `documents`), vous trouverez la structure standard suivante :

* **`models.py`** : Définition des tables de la base de données.
* **`serializers.py`** : Transformation des données Python en JSON (et inversement) avec validation métier.
* **`views.py`** : Logique des points d'entrée (Endpoints) de l'API.
* **`urls.py`** : Routage des requêtes HTTP vers les vues.
* **`signals.py`** : (Si présent) Automatisation des tâches, comme la création d'un dossier racine lors de l'ouverture d'un nouveau dossier client.

---

## 🛡️ Sécurité et API

* **Authentification** : Utilisation de **JWT (JSON Web Tokens)**. Le token doit être envoyé dans l'en-tête `Authorization: Bearer <token>`.
* **Permissions** : Les accès sont régis par des classes de permissions personnalisées (ex: seul l'avocat responsable d'un dossier peut modifier ses documents confidentiels).
* **Audit** : Chaque action de création, modification ou suppression déclenche une entrée dans le module `audit` pour répondre aux exigences de conformité du barreau.

---
