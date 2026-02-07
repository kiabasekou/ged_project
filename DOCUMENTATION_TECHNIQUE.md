# GED Cabinet Kiaba - Documentation Technique

## Systeme de Gestion Electronique de Documents pour Cabinets Juridiques

**Version:** 1.0.0
**Auteur:** Cabinet Kiaba
**Zone geographique:** Gabon (Libreville) / OHADA
**Conformite:** RGPD gabonais (Loi 001/2011 mod. 2023)

---

## Table des Matieres

1. [Presentation du Projet](#1-presentation-du-projet)
2. [Architecture Technique](#2-architecture-technique)
3. [Modeles de Donnees](#3-modeles-de-donnees)
4. [API REST](#4-api-rest)
5. [Frontend](#5-frontend)
6. [Securite et Conformite](#6-securite-et-conformite)
7. [Installation et Deploiement](#7-installation-et-deploiement)
8. [Variables d'Environnement](#8-variables-denvironnement)

---

## 1. Presentation du Projet

### 1.1 Objectif

Le projet GED Cabinet Kiaba est un systeme de gestion electronique de documents concu specifiquement pour les cabinets d'avocats et de notaires au Gabon et dans la zone OHADA. Il permet de :

- Gerer les dossiers juridiques et notariaux
- Organiser et securiser les documents avec versionnage
- Suivre les clients (personnes physiques et morales)
- Planifier les evenements (audiences, rendez-vous, formalites)
- Assurer une tracabilite complete (audit)
- Respecter la conformite RGPD gabonaise

### 1.2 Fonctionnalites Principales

| Module | Description |
|--------|-------------|
| **Utilisateurs** | Gestion des comptes avec roles (Avocat, Notaire, Stagiaire, etc.) |
| **Clients** | Base de donnees clients unifiee (personnes physiques/morales) |
| **Dossiers** | Gestion centralisee des affaires juridiques |
| **Documents** | GED avec versionnage, chiffrement et verification d'integrite |
| **Agenda** | Calendrier partage avec integration aux dossiers |
| **Audit** | Journal d'audit complet avec anonymisation RGPD |

---

## 2. Architecture Technique

### 2.1 Stack Technologique

#### Backend
| Technologie | Version | Role |
|-------------|---------|------|
| Python | 3.11+ | Langage |
| Django | 4.2.7 | Framework web |
| Django REST Framework | 3.14.0 | API REST |
| PostgreSQL | 15 | Base de donnees (production) |
| SQLite | 3 | Base de donnees (developpement) |
| Redis | 7 | Cache et file de messages |
| Celery | 5.3.4 | Taches asynchrones |
| SimpleJWT | 5.3.0 | Authentification JWT |
| django-guardian | 2.4.0 | Permissions par objet |

#### Frontend
| Technologie | Version | Role |
|-------------|---------|------|
| Vue.js | 3.5.24 | Framework JavaScript |
| Vuetify | 3.5.0 | Composants Material Design |
| Pinia | 3.0.4 | Gestion d'etat |
| Vue Router | 4.6.4 | Routage SPA |
| Axios | 1.13.2 | Client HTTP |
| FullCalendar | 6.1.20 | Calendrier interactif |
| ApexCharts | 5.3.6 | Graphiques |
| pdfjs-dist | 5.4.530 | Visualisation PDF |

#### Infrastructure
| Technologie | Role |
|-------------|------|
| Docker | Conteneurisation |
| Docker Compose | Orchestration |
| Nginx | Reverse proxy (production) |
| Gunicorn | Serveur WSGI |
| Daphne | Serveur ASGI (WebSockets) |

### 2.2 Structure du Projet

```
ged_project/
├── backend/                      # API Django
│   ├── apps/                     # Applications metier
│   │   ├── users/                # Gestion utilisateurs
│   │   ├── clients/              # Gestion clients
│   │   ├── dossiers/             # Gestion dossiers juridiques
│   │   ├── documents/            # GED et versionnage
│   │   ├── agenda/               # Calendrier
│   │   ├── audit/                # Journal d'audit
│   │   └── core/                 # Modeles de base
│   ├── config/                   # Configuration Django
│   ├── requirements.txt          # Dependances Python
│   └── manage.py                 # CLI Django
│
├── frontend/                     # SPA Vue.js
│   ├── src/
│   │   ├── components/           # Composants reutilisables
│   │   ├── views/                # Pages
│   │   ├── stores/               # Stores Pinia
│   │   ├── services/             # Services API
│   │   ├── plugins/              # Plugins (axios, vuetify)
│   │   ├── router/               # Configuration routeur
│   │   ├── composables/          # Hooks Vue 3
│   │   └── utils/                # Utilitaires
│   ├── package.json              # Dependances npm
│   └── vite.config.js            # Configuration Vite
│
├── docker/                       # Fichiers Docker
├── docker-compose.yml            # Orchestration
└── DOCUMENTATION_TECHNIQUE.md    # Ce fichier
```

---

## 3. Modeles de Donnees

### 3.1 User (Utilisateur)

**Fichier:** `backend/apps/users/models.py`

Modele utilisateur personnalise etendant `AbstractUser` de Django.

#### Champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique (PK) |
| `username` | CharField | Nom d'utilisateur (herite) |
| `email` | EmailField | Adresse email (herite) |
| `first_name` | CharField | Prenom (herite) |
| `last_name` | CharField | Nom (herite) |
| `role` | CharField | Role dans le cabinet |
| `professional_id` | CharField | Numero de carte professionnelle |
| `phone_number` | CharField | Telephone professionnel |
| `has_accepted_privacy_policy` | BooleanField | Acceptation RGPD |
| `privacy_policy_accepted_at` | DateTimeField | Date acceptation RGPD |
| `is_active` | BooleanField | Compte actif |
| `created_at` | DateTimeField | Date creation |
| `updated_at` | DateTimeField | Date modification |

#### Roles Disponibles

| Code | Label |
|------|-------|
| `ADMIN` | Administrateur systeme |
| `AVOCAT` | Avocat |
| `NOTAIRE` | Notaire |
| `CONSEIL_JURIDIQUE` | Conseil juridique |
| `STAGIAIRE` | Stagiaire / Collaborateur |
| `SECRETAIRE` | Secretaire / Clerc |
| `ASSISTANT` | Assistant juridique |

#### Proprietes

```python
@property
def is_legal_professional(self) -> bool:
    """Retourne True si avocat, notaire ou conseil juridique"""

@property
def is_admin_or_professional(self) -> bool:
    """Retourne True si staff ou professionnel juridique"""
```

---

### 3.2 Client

**Fichier:** `backend/apps/clients/models.py`

Modele unifie pour personnes physiques et morales.

#### Champs Communs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique (PK) |
| `client_type` | CharField | Type: PHYSIQUE ou MORALE |
| `email` | EmailField | Email principal (unique) |
| `phone_primary` | CharField | Telephone principal |
| `phone_secondary` | CharField | Telephone secondaire |
| `address_line` | CharField | Rue / BP |
| `neighborhood` | CharField | Quartier |
| `city` | CharField | Ville (defaut: Libreville) |
| `country` | CharField | Pays (defaut: Gabon) |
| `consent_given` | BooleanField | Consentement RGPD |
| `consent_date` | DateTimeField | Date consentement |
| `retention_period_years` | PositiveIntegerField | Duree conservation (defaut: 10 ans) |
| `is_active` | BooleanField | Client actif |
| `notes` | TextField | Notes internes |
| `created_at` | DateTimeField | Date creation |
| `updated_at` | DateTimeField | Date modification |

#### Champs Personne Physique

| Champ | Type | Description |
|-------|------|-------------|
| `first_name` | CharField | Prenom(s) |
| `last_name` | CharField | Nom de famille |
| `date_of_birth` | DateField | Date de naissance |
| `place_of_birth` | CharField | Lieu de naissance |
| `ni_number` | CharField | N CNI / Passeport |
| `ni_type` | CharField | Type de piece (CNI/PASSPORT) |

#### Champs Personne Morale

| Champ | Type | Description |
|-------|------|-------------|
| `company_name` | CharField | Raison sociale |
| `rccm` | CharField | N RCCM (format: GA-LBV-2024-A12-00567) |
| `nif` | CharField | N Identifiant Fiscal (format: XXXXXX-L) |
| `representative_name` | CharField | Nom representant legal |
| `representative_role` | CharField | Fonction representant |

#### Proprietes

```python
@property
def display_name(self) -> str:
    """Nom affiche (raison sociale ou nom complet)"""

@property
def full_address(self) -> str:
    """Adresse complete formatee"""

@property
def is_individual(self) -> bool:
    """True si personne physique"""

@property
def is_company(self) -> bool:
    """True si personne morale"""
```

---

### 3.3 Dossier

**Fichier:** `backend/apps/dossiers/models.py`

Modele central representant un dossier juridique ou notarial.

#### Champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique (PK) |
| `client` | ForeignKey | Client (PROTECT) |
| `responsible` | ForeignKey | Responsable principal (User) |
| `assigned_users` | ManyToManyField | Collaborateurs autorises |
| `title` | CharField | Intitule du dossier |
| `reference_code` | CharField | Reference auto (GAB-YYYY-NNNN) |
| `category` | CharField | Categorie juridique |
| `status` | CharField | Statut du dossier |
| `description` | TextField | Resume et notes |
| `opponent` | CharField | Partie adverse |
| `jurisdiction` | CharField | Juridiction / Tribunal |
| `critical_deadline` | DateField | Delai critique |
| `legal_basis` | CharField | Base legale (RGPD) |
| `retention_period_years` | PositiveIntegerField | Duree conservation |
| `opening_date` | DateField | Date ouverture |
| `closing_date` | DateField | Date cloture |
| `archived_date` | DateTimeField | Date archivage |
| `created_at` | DateTimeField | Date creation |
| `updated_at` | DateTimeField | Date modification |

#### Statuts

| Code | Label |
|------|-------|
| `OUVERT` | Ouvert / En cours |
| `ATTENTE` | En attente de pieces ou decision |
| `SUSPENDU` | Suspendu |
| `CLOTURE` | Cloture |
| `ARCHIVE` | Archive |

#### Categories

| Code | Label | Type |
|------|-------|------|
| `CONTENTIEUX` | Contentieux (civil, penal, administratif) | Avocat |
| `CONSEIL` | Conseil juridique / Avis | Avocat |
| `RECOUVREMENT` | Recouvrement de creances | Avocat |
| `TRAVAIL` | Droit du travail | Avocat |
| `IMMOBILIER` | Actes immobiliers / Foncier | Notaire |
| `SUCCESSION` | Succession / Partage | Notaire |
| `MARIAGE` | Contrat de mariage | Notaire |
| `DONATION` | Donation / Liberalite | Notaire |
| `SOCIETE` | Constitution / Modification societe OHADA | Notaire |
| `FAMILLE` | Divorce, garde, filiation | Commun |
| `COMMERCIAL` | Droit commercial OHADA | Commun |
| `AUTRE` | Autre | Commun |

#### Proprietes et Methodes

```python
@property
def is_overdue(self) -> bool:
    """True si delai critique depasse"""

@property
def full_reference(self) -> str:
    """Reference complete du dossier"""

def generate_reference_code(self) -> str:
    """Genere une reference unique GAB-YYYY-NNNN"""
```

---

### 3.4 Document

**Fichier:** `backend/apps/documents/models.py`

Document avec versionnage immuable et chiffrement.

#### Champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique (PK) |
| `dossier` | ForeignKey | Dossier juridique |
| `folder` | ForeignKey | Sous-dossier (Folder) |
| `uploaded_by` | ForeignKey | Utilisateur ayant uploade |
| `file` | FileField | Fichier (stockage chiffre) |
| `title` | CharField | Titre du document |
| `description` | TextField | Description |
| `original_filename` | CharField | Nom original |
| `file_extension` | CharField | Extension (.pdf, .docx, etc.) |
| `file_size` | BigIntegerField | Taille en octets |
| `mime_type` | CharField | Type MIME |
| `file_hash` | CharField | Hash SHA-256 (integrite) |
| `version` | PositiveIntegerField | Numero de version |
| `is_current_version` | BooleanField | Version actuelle |
| `previous_version` | ForeignKey | Version precedente (self) |
| `sensitivity` | CharField | Niveau de sensibilite |
| `retention_until` | DateField | Date de conservation |
| `uploaded_at` | DateTimeField | Date upload |
| `updated_at` | DateTimeField | Date modification |

#### Niveaux de Sensibilite

| Code | Label |
|------|-------|
| `public` | Public |
| `internal` | Usage Interne |
| `confidential` | Confidentiel |
| `secret` | Secret Professionnel |

#### Extensions Autorisees

```python
ALLOWED_EXTENSIONS = [
    '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
    '.txt', '.rtf', '.odt', '.ods', '.odp',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
    '.zip', '.rar', '.7z', '.msg', '.eml'
]
```

#### Methodes

```python
def create_new_version(self, new_file, uploaded_by, **metadata) -> Document:
    """Cree une nouvelle version du document"""

def get_version_history(self) -> list:
    """Retourne la chaine complete des versions"""

def verify_integrity(self) -> bool:
    """Verifie que le fichier n'a pas ete altere"""
```

---

### 3.5 Folder

**Fichier:** `backend/apps/documents/models.py`

Structure hierarchique pour organiser les documents.

#### Champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique (PK) |
| `name` | CharField | Nom du dossier |
| `dossier` | ForeignKey | Dossier juridique parent |
| `parent` | ForeignKey | Dossier parent (self) |
| `created_by` | ForeignKey | Utilisateur createur |
| `created_at` | DateTimeField | Date creation |

#### Methodes

```python
def get_full_path(self) -> str:
    """Retourne le chemin complet du dossier"""
```

---

### 3.6 Event

**Fichier:** `backend/apps/agenda/models.py`

Evenement calendrier du cabinet.

#### Champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique (PK) |
| `title` | CharField | Titre |
| `type` | CharField | Type d'evenement |
| `start_date` | DateField | Date de debut |
| `start_time` | TimeField | Heure de debut |
| `all_day` | BooleanField | Journee entiere |
| `end_date` | DateField | Date de fin |
| `end_time` | TimeField | Heure de fin |
| `location` | CharField | Lieu |
| `description` | TextField | Description / Notes |
| `dossier` | ForeignKey | Dossier lie (optionnel) |
| `created_by` | ForeignKey | Createur |
| `created_at` | DateTimeField | Date creation |
| `updated_at` | DateTimeField | Date modification |

#### Types d'Evenements

| Code | Label | Couleur |
|------|-------|---------|
| `AUDIENCE` | Audience / Plaidoirie | Rouge (#D32F2F) |
| `RDV` | Rendez-vous client | Bleu fonce (#1A237E) |
| `FORMALITE` | Formalite notariale | Orange (#FF8F00) |
| `CONGE` | Conge / Absence | Gris (#616161) |
| `AUTRE` | Autre evenement | Bleu (#1976D2) |

---

### 3.7 AuditLog

**Fichier:** `backend/apps/audit/models.py`

Journal d'audit avec anonymisation RGPD.

#### Champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique (PK) |
| `user` | ForeignKey | Utilisateur (SET_NULL) |
| `content_type` | ForeignKey | Type d'objet (ContentType) |
| `object_id` | UUIDField | ID de l'objet |
| `object_repr` | CharField | Representation textuelle |
| `action_type` | CharField | Type d'action |
| `changes` | JSONField | Changements (anonymises) |
| `sensitive_fields_hash` | JSONField | Hash des champs sensibles |
| `description` | TextField | Description |
| `ip_address` | GenericIPAddressField | Adresse IP |
| `user_agent` | TextField | User Agent |
| `request_path` | CharField | Chemin de la requete |
| `session_key` | CharField | Cle de session |
| `timestamp` | DateTimeField | Horodatage |

#### Types d'Actions

| Code | Label |
|------|-------|
| `CREATE` | Creation |
| `READ` | Lecture |
| `UPDATE` | Modification |
| `DELETE` | Suppression |
| `DOWNLOAD` | Telechargement |
| `UPLOAD` | Upload |
| `RESTORE` | Restauration |
| `INTEGRITY_CHECK` | Verification Integrite |
| `INTEGRITY_FAILURE` | Echec Integrite |
| `LOGIN` | Connexion |
| `LOGOUT` | Deconnexion |
| `LOGIN_FAILED` | Echec Connexion |
| `PERMISSION_DENIED` | Acces Refuse |

#### Champs Sensibles Anonymises

```python
SENSITIVE_FIELDS = [
    'ni_number', 'nif', 'rccm', 'date_of_birth', 'place_of_birth',
    'email', 'phone_primary', 'phone_secondary', 'address_line',
    'password', 'social_security', 'bank_account'
]
```

---

## 4. API REST

### 4.1 Authentification

Base URL: `/api/`

#### Endpoints JWT

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/token/` | Obtenir tokens (access + refresh) |
| POST | `/token/refresh/` | Rafraichir access token |
| POST | `/token/verify/` | Verifier validite du token |

**Request POST /token/**
```json
{
  "username": "avocat@cabinet.ga",
  "password": "secret123"
}
```

**Response 200**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 4.2 Users API

Base URL: `/api/users/`

| Methode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/` | Liste des utilisateurs | Admin |
| GET | `/{id}/` | Detail utilisateur | Admin |
| GET | `/me/` | Profil connecte | Authentifie |
| PATCH | `/{id}/` | Modifier utilisateur | Admin |
| PATCH | `/update-profile/` | Modifier son profil | Authentifie |

---

### 4.3 Clients API

Base URL: `/api/clients/`

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste des clients (paginee, filtrable) |
| POST | `/` | Creer un client |
| GET | `/{id}/` | Detail client |
| PATCH | `/{id}/` | Modifier client |
| DELETE | `/{id}/` | Soft delete client |
| POST | `/{id}/grant-consent/` | Enregistrer consentement RGPD |
| GET | `/stats/` | Statistiques clients |

#### Filtres Disponibles

| Parametre | Type | Description |
|-----------|------|-------------|
| `client_type` | exact | PHYSIQUE ou MORALE |
| `city` | exact, icontains | Ville |
| `neighborhood` | exact, icontains | Quartier |
| `is_active` | exact | Actif ou non |
| `consent_given` | exact | Consentement RGPD |
| `created_at` | gte, lte | Date creation |

#### Recherche

| Champ searchable |
|------------------|
| `first_name`, `last_name`, `company_name` |
| `rccm`, `nif`, `ni_number` |
| `email`, `phone_primary`, `phone_secondary` |
| `representative_name` |

---

### 4.4 Dossiers API

Base URL: `/api/dossiers/`

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste des dossiers (filtrable) |
| POST | `/` | Creer un dossier |
| GET | `/{id}/` | Detail dossier |
| PATCH | `/{id}/` | Modifier dossier |
| POST | `/{id}/cloturer/` | Cloturer dossier |
| POST | `/{id}/archiver/` | Archiver dossier |
| POST | `/{id}/assign-user/` | Ajouter collaborateur |
| POST | `/{id}/remove-user/` | Retirer collaborateur |
| GET | `/{id}/collaborateurs/` | Liste collaborateurs |
| GET | `/stats/` | Statistiques dossiers |

#### Filtres Disponibles

| Parametre | Type | Description |
|-----------|------|-------------|
| `status` | exact, in | Statut(s) |
| `category` | exact, in | Categorie(s) |
| `client` | exact | UUID client |
| `responsible` | exact | UUID responsable |
| `critical_deadline` | gte, lte | Delai critique |
| `opening_date` | gte, lte, year | Date ouverture |

#### Recherche

| Champ searchable |
|------------------|
| `=reference_code` (exact) |
| `^title` (startswith) |
| `description` |
| `client__last_name`, `client__company_name`, `client__nif` |

#### Response GET /stats/

```json
{
  "total": 150,
  "ouverts": 45,
  "en_attente": 12,
  "en_retard": 5,
  "clotures": 78,
  "archives": 15,
  "par_categorie": {
    "CONTENTIEUX": 30,
    "CONSEIL": 25,
    "IMMOBILIER": 40,
    "SUCCESSION": 20
  },
  "par_statut": {
    "OUVERT": 45,
    "ATTENTE": 12,
    "CLOTURE": 78,
    "ARCHIVE": 15
  }
}
```

---

### 4.5 Documents API

Base URL: `/api/documents/`

#### Folders

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/folders/` | Liste des folders |
| POST | `/folders/` | Creer un folder |
| GET | `/folders/{id}/` | Detail folder |
| PATCH | `/folders/{id}/` | Modifier folder |
| DELETE | `/folders/{id}/` | Supprimer folder |

#### Documents

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/documents/` | Liste des documents |
| POST | `/documents/` | Upload document |
| GET | `/documents/{id}/` | Detail document |
| PATCH | `/documents/{id}/` | Modifier metadonnees |
| DELETE | `/documents/{id}/` | Supprimer document |
| GET | `/documents/{id}/download/` | Telecharger document |
| POST | `/documents/{id}/new_version/` | Nouvelle version |
| GET | `/documents/{id}/history/` | Historique versions |
| POST | `/documents/{id}/verify-integrity/` | Verifier integrite |
| POST | `/documents/{id}/restore-version/` | Restaurer version |
| GET | `/documents/stats/` | Statistiques documents |

#### Upload Document (multipart/form-data)

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `file` | File | Oui | Fichier a uploader |
| `dossier` | UUID | Oui | UUID du dossier |
| `folder` | UUID | Non | UUID du folder |
| `title` | String | Oui | Titre du document |
| `description` | String | Non | Description |
| `sensitivity` | String | Non | Niveau (defaut: internal) |

---

### 4.6 Agenda API

Base URL: `/api/agenda/`

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste des evenements |
| POST | `/` | Creer evenement |
| GET | `/{id}/` | Detail evenement |
| PATCH | `/{id}/` | Modifier evenement |
| DELETE | `/{id}/` | Supprimer evenement |

---

### 4.7 Audit API

Base URL: `/api/audit/`

| Methode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/` | Liste des logs | Admin |
| GET | `/{id}/` | Detail log | Admin |

---

## 5. Frontend

### 5.1 Stores Pinia

#### authStore (`stores/auth.js`)

| State | Type | Description |
|-------|------|-------------|
| `user` | Object | Utilisateur connecte |
| `token` | String | Access token JWT |
| `loading` | Boolean | Chargement en cours |

| Action | Description |
|--------|-------------|
| `login(credentials)` | Connexion |
| `fetchMe()` | Recuperer profil |
| `initialize()` | Initialiser depuis localStorage |
| `logout()` | Deconnexion |

#### dossierStore (`stores/dossier.js`)

| State | Type | Description |
|-------|------|-------------|
| `list` | Array | Liste des dossiers |
| `current` | Object | Dossier courant |
| `loading` | Boolean | Chargement en cours |
| `stats` | Object | Statistiques |
| `pagination` | Object | Pagination |

| Action | Description |
|--------|-------------|
| `fetchList(params)` | Charger liste |
| `fetchStats()` | Charger statistiques |
| `fetchDossier(id)` | Charger detail |
| `createDossier(data)` | Creer dossier |
| `updateDossier(id, data)` | Modifier dossier |
| `closeDossier(id)` | Cloturer dossier |
| `archiveDossier(id)` | Archiver dossier |

#### documentStore (`stores/document.js`)

| State | Type | Description |
|-------|------|-------------|
| `documents` | Array | Liste des documents |
| `currentDocument` | Object | Document courant |
| `uploadProgress` | Number | Progression upload |

| Action | Description |
|--------|-------------|
| `fetchList(params)` | Charger liste |
| `upload(formData, onProgress)` | Upload document |
| `download(id, filename)` | Telecharger |
| `createVersion(id, formData)` | Nouvelle version |

### 5.2 Services API

| Service | Fichier | Description |
|---------|---------|-------------|
| `dossierService` | `services/dossierService.js` | Operations dossiers |
| `documentService` | `services/documentService.js` | Operations documents |
| `clientService` | `services/clientService.js` | Operations clients |
| `agendaService` | `services/agendaService.js` | Operations evenements |

### 5.3 Configuration Axios

**Fichier:** `plugins/axios.js`

- Base URL configurable via `VITE_API_BASE_URL`
- Injection automatique du token JWT
- Gestion du refresh token automatique
- File d'attente pour requetes pendant le refresh

---

## 6. Securite et Conformite

### 6.1 Authentification

- **JWT (JSON Web Tokens)** via SimpleJWT
- Access token : duree courte (5-15 min recommande)
- Refresh token : duree longue (7 jours)
- Stockage cote client : localStorage

### 6.2 Autorisation

- **RBAC** : Controle d'acces base sur les roles
- **Permissions par objet** : django-guardian
- Roles hierarchiques avec permissions specifiques

### 6.3 Protection des Donnees (RGPD)

| Mesure | Description |
|--------|-------------|
| **Anonymisation** | Champs sensibles anonymises dans les logs d'audit |
| **Consentement** | Tracking du consentement client |
| **Retention** | Duree de conservation configurable |
| **Chiffrement** | Stockage chiffre des documents (Fernet) |
| **Integrite** | Hash SHA-256 pour verification |

### 6.4 Validation des Fichiers

- Verification de l'extension
- Verification du type MIME
- Verification des magic bytes (anti-malware basique)
- Taille maximale : 100 MB

---

## 7. Installation et Deploiement

### 7.1 Prerequis

- Python 3.11+
- Node.js 18+
- PostgreSQL 15 (production)
- Redis 7 (optionnel)
- Docker et Docker Compose (recommande)

### 7.2 Installation Developpement

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou .\venv\Scripts\activate  # Windows

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 7.3 Deploiement Docker

```bash
docker-compose up -d
```

Services demarres :
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend Django (port 8000)
- Frontend Vue.js (port 3000)

---

## 8. Variables d'Environnement

### 8.1 Backend (.env)

| Variable | Description | Defaut |
|----------|-------------|--------|
| `SECRET_KEY` | Cle secrete Django | (obligatoire en prod) |
| `DEBUG` | Mode debug | True |
| `ALLOWED_HOSTS` | Hotes autorises | localhost,127.0.0.1 |
| `DATABASE_URL` | URL PostgreSQL | sqlite:///db.sqlite3 |
| `USE_SQLITE` | Utiliser SQLite | True |
| `REDIS_URL` | URL Redis | redis://localhost:6379 |
| `CORS_ALLOWED_ORIGINS` | Origines CORS | localhost:3000,5173,8080 |
| `ENCRYPTION_KEY` | Cle Fernet (chiffrement) | (obligatoire) |
| `EMAIL_BACKEND` | Backend email | console |
| `MAX_UPLOAD_SIZE` | Taille max upload | 104857600 (100MB) |

### 8.2 Frontend (.env)

| Variable | Description | Defaut |
|----------|-------------|--------|
| `VITE_API_BASE_URL` | URL de l'API | /api |
| `VITE_APP_TITLE` | Titre application | GED Cabinet Kiaba |

---

## Diagramme Relationnel

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Client      │
├─────────────────┤       ├─────────────────┤
│ id (UUID)       │       │ id (UUID)       │
│ username        │       │ client_type     │
│ role            │       │ first_name      │
│ professional_id │       │ last_name       │
└────────┬────────┘       │ company_name    │
         │                │ email           │
         │                └────────┬────────┘
         │                         │
         │    ┌────────────────────┼────────────────────┐
         │    │                    │                    │
         ▼    ▼                    ▼                    │
┌─────────────────┐       ┌─────────────────┐          │
│     Dossier     │◄──────│     Event       │          │
├─────────────────┤       ├─────────────────┤          │
│ id (UUID)       │       │ id (UUID)       │          │
│ reference_code  │       │ title           │          │
│ title           │       │ type            │          │
│ category        │       │ start_date      │          │
│ status          │       │ dossier (FK)    │          │
│ client (FK)     │◄──────┴─────────────────┘          │
│ responsible (FK)│                                     │
│ assigned_users  │                                     │
└────────┬────────┘                                     │
         │                                              │
         │                                              │
         ▼                                              │
┌─────────────────┐       ┌─────────────────┐          │
│     Folder      │       │    Document     │          │
├─────────────────┤       ├─────────────────┤          │
│ id (UUID)       │◄──────│ id (UUID)       │          │
│ name            │       │ title           │          │
│ dossier (FK)    │       │ file            │          │
│ parent (FK)     │       │ file_hash       │          │
│ created_by (FK) │       │ version         │          │
└─────────────────┘       │ dossier (FK)    │          │
                          │ folder (FK)     │          │
                          │ uploaded_by (FK)│          │
                          │ previous_version│          │
                          └─────────────────┘          │
                                                       │
┌─────────────────┐                                    │
│    AuditLog     │◄───────────────────────────────────┘
├─────────────────┤    (Logs toutes les entites)
│ id (UUID)       │
│ user (FK)       │
│ content_type    │
│ object_id       │
│ action_type     │
│ changes (JSON)  │
│ timestamp       │
└─────────────────┘
```

---

## Support et Contact

- **Repository:** https://github.com/kiabasekou/ged_project
- **Issues:** https://github.com/kiabasekou/ged_project/issues

---

*Document genere automatiquement - Cabinet Kiaba GED v1.0.0*
