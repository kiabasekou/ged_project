voici une note stratégique sur la gestion des versions au sein de votre GED. Pour un cabinet d'avocats, la traçabilité n'est pas une option : c'est une preuve de rigueur déontologique.

Cette documentation explique comment votre système garantit qu'aucune information n'est jamais perdue, même en cas de modification d'une pièce.

---

# 📑 Stratégie de Versionnage des Documents

Dans le cadre de la **GED Cabinet**, nous avons adopté une approche de **versionnage immuable**. Contrairement à un système de fichiers classique qui écrase les données, notre architecture conserve l'historique complet de chaque document.

## ⚙️ Mécanisme de Fonctionnement

Chaque mise à jour d'un document ne modifie pas le fichier existant, mais crée une nouvelle instance dans la base de données.

| Champ | Rôle Technique |
| --- | --- |
| **`version`** | Un entier incrémenté automatiquement (v1, v2, v3...). |
| **`is_current_version`** | Un booléen (Vrai/Faux) qui indique quelle version est la référence actuelle. |
| **`previous_version`** | Un lien (Clé étrangère) vers la version immédiatement précédente. |
| **`file_hash`** | L'empreinte numérique (SHA-256) unique du fichier pour garantir son intégrité. |

---

## 🔄 Flux de Travail : Mise à jour d'une pièce

Lorsqu'un collaborateur téléverse une nouvelle version d'une pièce de procédure (ex: un mémoire en défense) :

1. **Calcul de l'empreinte** : Le Backend calcule le hachage du nouveau fichier.
2. **Archivage de l'ancienne** : L'ancienne version voit son champ `is_current_version` passer à `False`.
3. **Création du lien** : La nouvelle version est enregistrée avec `is_current_version = True` et pointe vers l'ancienne via `previous_version`.
4. **Incrémentation** : Le numéro de version passe de  à .

---

## ⚖️ Bénéfices Juridiques et Techniques

### 1. Intégrité de la Preuve

Grâce au hachage SHA-256, nous pouvons prouver devant un tribunal ou un expert que le document n'a subi aucune altération entre son upload et sa consultation. Si le fichier physique est modifié manuellement sur le serveur, le hachage ne correspondra plus, alertant immédiatement l'administrateur.

### 2. Audit de Modification

Chaque version est liée à un utilisateur (`uploaded_by`) et possède son propre horodatage (`uploaded_at`). Le cabinet sait exactement qui a produit quelle version du document et à quel moment.

### 3. Récupération de Données (Rollback)

En cas d'erreur de manipulation (upload du mauvais fichier), il est possible de restaurer une version précédente en un clic, sans perte de données.

---

## 🛠️ Implémentation dans l'API

* **Lecture** : Par défaut, le Endpoint `/api/documents/` ne renvoie que les documents où `is_current_version=True`.
* **Historique** : Un Endpoint spécifique `/api/documents/{id}/history/` permet de récupérer la "chaîne de vie" du document pour l'afficher dans l'interface Vue.js.

---

### ✅ Conclusion de la mise en place

Maître, avec cette stratégie, votre GED ne se contente pas de stocker des fichiers : elle sécurise le patrimoine intellectuel de votre cabinet.


frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/
│   │   ├── logo.png
│   │   └── cabinet-bg.jpg          # Image de fond login
│   ├── components/                  # Composants réutilisables
│   │   ├── common/
│   │   │   ├── AppCard.vue
│   │   │   ├── AppAlert.vue
│   │   │   └── LoadingSpinner.vue
│   │   ├── layout/
│   │   │   ├── Sidebar.vue
│   │   │   ├── Header.vue
│   │   │   └── Footer.vue
│   │   └── dossier/
│   │       ├── DossierCard.vue
│   │       ├── DocumentTree.vue
│   │       └── DocumentItem.vue
│   ├── layouts/
│   │   └── DefaultLayout.vue        # Layout principal avec sidebar
│   ├── views/
│   │   ├── Auth/
│   │   │   └── LoginView.vue
│   │   ├── DashboardView.vue
│   │   ├── Client/
│   │   │   ├── ClientListView.vue
│   │   │   └── ClientDetailView.vue
│   │   └── Dossier/
│   │       ├── DossierListView.vue
│   │       ├── DossierCreateView.vue
│   │       └── DossierDetailView.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── auth.js
│   │   ├── dossier.js
│   │   └── client.js
│   ├── plugins/
│   │   ├── axios.js
│   │   └── vuetify.js
│   ├── utils/
│   │   ├── api.js                   # Wrapper Axios pour endpoints
│   │   └── format.js                # Formatage dates, tailles fichiers, etc.
│   ├── App.vue
│   └── main.js
├── vite.config.js
├── package.json
└── .env                             # Variables d'environnement (VITE_API_BASE_URL)



=== Application: django.contrib.admin ===

--- Modèle: LogEntry ---
Table: django_admin_log
Champs:
  - id (AutoField)
  - action_time (DateTimeField)
  - user (ForeignKey), relation -> User
  - content_type (ForeignKey), relation -> ContentType
  - object_id (TextField)
  - object_repr (CharField), max_length=200
  - action_flag (PositiveSmallIntegerField)
  - change_message (TextField)

=== Application: django.contrib.auth ===

--- Modèle: Permission ---
Table: auth_permission
Champs:
  - group (ManyToManyRel), relation -> Group
  - userobjectpermission (ManyToOneRel), relation -> UserObjectPermission
  - groupobjectpermission (ManyToOneRel), relation -> GroupObjectPermission
  - user (ManyToManyRel), relation -> User
  - id (AutoField)
  - name (CharField), max_length=255
  - content_type (ForeignKey), relation -> ContentType
  - codename (CharField), max_length=100

--- Modèle: Group ---
Table: auth_group
Champs:
  - groupobjectpermission (ManyToOneRel), relation -> GroupObjectPermission
  - user (ManyToManyRel), relation -> User
  - id (AutoField)
  - name (CharField), max_length=150
  - permissions (ManyToManyField), relation -> Permission

=== Application: django.contrib.contenttypes ===

--- Modèle: ContentType ---
Table: django_content_type
Champs:
  - logentry (ManyToOneRel), relation -> LogEntry
  - permission (ManyToOneRel), relation -> Permission
  - userobjectpermission (ManyToOneRel), relation -> UserObjectPermission
  - groupobjectpermission (ManyToOneRel), relation -> GroupObjectPermission
  - auditlog (ManyToOneRel), relation -> AuditLog
  - id (AutoField)
  - app_label (CharField), max_length=100
  - model (CharField), max_length=100

=== Application: django.contrib.sessions ===

--- Modèle: Session ---
Table: django_session
Champs:
  - session_key (CharField), max_length=40
  - session_data (TextField)
  - expire_date (DateTimeField)

=== Application: django.contrib.messages ===

=== Application: django.contrib.staticfiles ===

=== Application: guardian ===

--- Modèle: UserObjectPermission ---
Table: guardian_userobjectpermission
Champs:
  - id (AutoField)
  - permission (ForeignKey), relation -> Permission
  - content_type (ForeignKey), relation -> ContentType
  - object_pk (CharField), max_length=255
  - user (ForeignKey), relation -> User
  - content_object (GenericForeignKey)

--- Modèle: GroupObjectPermission ---
Table: guardian_groupobjectpermission
Champs:
  - id (AutoField)
  - permission (ForeignKey), relation -> Permission
  - content_type (ForeignKey), relation -> ContentType
  - object_pk (CharField), max_length=255
  - group (ForeignKey), relation -> Group
  - content_object (GenericForeignKey)

=== Application: rest_framework ===

=== Application: rest_framework_simplejwt ===

=== Application: corsheaders ===

=== Application: django_filters ===

=== Application: rest_framework_guardian ===

=== Application: apps.core ===

=== Application: apps.users ===

--- Modèle: User ---
Table: users_user
Champs:
  - logentry (ManyToOneRel), relation -> LogEntry
  - userobjectpermission (ManyToOneRel), relation -> UserObjectPermission
  - managed_dossiers (ManyToOneRel), relation -> Dossier
  - accessible_dossiers (ManyToManyRel), relation -> Dossier
  - created_folders (ManyToOneRel), relation -> Folder
  - uploaded_documents (ManyToOneRel), relation -> Document
  - audit_logs (ManyToOneRel), relation -> AuditLog
  - created_events (ManyToOneRel), relation -> Event
  - password (CharField), max_length=128
  - last_login (DateTimeField)
  - is_superuser (BooleanField)
  - username (CharField), max_length=150
  - first_name (CharField), max_length=150
  - last_name (CharField), max_length=150
  - email (EmailField), max_length=254
  - is_staff (BooleanField)
  - date_joined (DateTimeField)
  - id (UUIDField), max_length=32
  - role (CharField), max_length=20
  - professional_id (CharField), max_length=50
  - phone_number (CharField), max_length=20
  - has_accepted_privacy_policy (BooleanField)
  - privacy_policy_accepted_at (DateTimeField)
  - created_at (DateTimeField)
  - updated_at (DateTimeField)
  - is_active (BooleanField)
  - groups (ManyToManyField), relation -> Group
  - user_permissions (ManyToManyField), relation -> Permission

=== Application: apps.clients ===

--- Modèle: Client ---
Table: clients_client
Champs:
  - dossiers (ManyToOneRel), relation -> Dossier
  - id (UUIDField), max_length=32
  - client_type (CharField), max_length=10
  - first_name (CharField), max_length=150
  - last_name (CharField), max_length=150
  - date_of_birth (DateField)
  - place_of_birth (CharField), max_length=150
  - ni_number (CharField), max_length=50
  - ni_type (CharField), max_length=20
  - company_name (CharField), max_length=255
  - rccm (CharField), max_length=50
  - nif (CharField), max_length=10
  - representative_name (CharField), max_length=255
  - representative_role (CharField), max_length=100
  - email (EmailField), max_length=254
  - phone_primary (CharField), max_length=20
  - phone_secondary (CharField), max_length=20
  - address_line (CharField), max_length=255
  - neighborhood (CharField), max_length=100
  - city (CharField), max_length=100
  - country (CharField), max_length=100
  - data_source (CharField), max_length=255
  - consent_given (BooleanField)
  - consent_date (DateTimeField)
  - retention_period_years (PositiveIntegerField)
  - created_at (DateTimeField)
  - updated_at (DateTimeField)
  - is_active (BooleanField)
  - notes (TextField)

=== Application: apps.dossiers ===

--- Modèle: Dossier ---
Table: dossiers_dossier
Champs:
  - folders (ManyToOneRel), relation -> Folder
  - documents (ManyToOneRel), relation -> Document
  - events (ManyToOneRel), relation -> Event
  - id (UUIDField), max_length=32
  - client (ForeignKey), relation -> Client
  - responsible (ForeignKey), relation -> User
  - title (CharField), max_length=300
  - reference_code (CharField), max_length=30
  - category (CharField), max_length=20
  - status (CharField), max_length=15
  - description (TextField)
  - opponent (CharField), max_length=255
  - jurisdiction (CharField), max_length=200
  - critical_deadline (DateField)
  - legal_basis (CharField), max_length=255
  - retention_period_years (PositiveIntegerField)
  - opening_date (DateField)
  - closing_date (DateField)
  - archived_date (DateTimeField)
  - created_at (DateTimeField)
  - updated_at (DateTimeField)
  - assigned_users (ManyToManyField), relation -> User

=== Application: apps.documents ===

--- Modèle: Folder ---
Table: documents_folder
Champs:
  - subfolders (ManyToOneRel), relation -> Folder
  - documents (ManyToOneRel), relation -> Document
  - id (UUIDField), max_length=32
  - name (CharField), max_length=150
  - dossier (ForeignKey), relation -> Dossier
  - parent (ForeignKey), relation -> Folder
  - created_at (DateTimeField)
  - created_by (ForeignKey), relation -> User

--- Modèle: Document ---
Table: documents_document
Champs:
  - next_versions (ManyToOneRel), relation -> Document
  - id (UUIDField), max_length=32
  - dossier (ForeignKey), relation -> Dossier
  - folder (ForeignKey), relation -> Folder
  - uploaded_by (ForeignKey), relation -> User
  - file (FileField), max_length=100
  - title (CharField), max_length=300
  - description (TextField)
  - original_filename (CharField), max_length=255
  - file_extension (CharField), max_length=10
  - file_size (BigIntegerField)
  - mime_type (CharField), max_length=100
  - file_hash (CharField), max_length=64
  - version (PositiveIntegerField)
  - is_current_version (BooleanField)
  - previous_version (ForeignKey), relation -> Document
  - sensitivity (CharField), max_length=20
  - retention_until (DateField)
  - uploaded_at (DateTimeField)
  - updated_at (DateTimeField)

=== Application: apps.audit ===

--- Modèle: AuditLog ---
Table: audit_auditlog
Champs:
  - id (UUIDField), max_length=32
  - user (ForeignKey), relation -> User
  - content_type (ForeignKey), relation -> ContentType
  - object_id (UUIDField), max_length=32
  - object_repr (CharField), max_length=255
  - action_type (CharField), max_length=20
  - changes (JSONField)
  - description (TextField)
  - ip_address (GenericIPAddressField), max_length=39
  - user_agent (TextField)
  - request_path (CharField), max_length=500
  - session_key (CharField), max_length=40
  - timestamp (DateTimeField)
  - content_object (GenericForeignKey)

=== Application: apps.agenda ===

--- Modèle: Event ---
Table: agenda_event
Champs:
  - id (UUIDField), max_length=32
  - title (CharField), max_length=255
  - type (CharField), max_length=20
  - start_date (DateField)
  - start_time (TimeField)
  - all_day (BooleanField)
  - end_date (DateField)
  - end_time (TimeField)
  - location (CharField), max_length=255
  - description (TextField)
  - dossier (ForeignKey), relation -> Dossier
  - created_by (ForeignKey), relation -> User
  - created_at (DateTimeField)
  - updated_at (DateTimeField)
