# CLAUDE.md - Directives Projet GED Cabinet

## 🎯 Objectifs
- Centraliser et sécuriser les documents juridiques des clients.
- Garantir la conformité RGPD et loi gabonaise sur la protection des données.
- Maintenir une architecture monorepo claire et évolutive.

---

## 🛠️ Backend (Django + DRF)
- Respecter **PEP8** et utiliser **Black** pour le formatage.
- Authentification via **JWT (SimpleJWT)**, avec rotation des tokens et refresh sécurisé.
- Base de données :
  - **SQLite** uniquement pour développement local.
  - **PostgreSQL** obligatoire en production.
- Activer **Django Security Middleware** (XSS, CSRF, HSTS).
- Journaliser toutes les actions sensibles (accès, modification, suppression de documents).
- Tests unitaires et d’intégration avec **pytest-django** (couverture ≥ 90 %).

---

## 🎨 Frontend (Vue.js + Vuetify + Pinia)
- Utiliser **Composition API** pour tous les composants.
- Respecter une arborescence claire : `components/`, `views/`, `store/`.
- Gestion d’état centralisée avec **Pinia** (pas de state local pour les données critiques).
- Axios configuré avec **intercepteurs JWT** (refresh automatique).
- UI conforme aux standards d’accessibilité (WCAG 2.1 AA).
- Tests avec **Vitest** et **Cypress** pour E2E.

---

## 🔒 Sécurité & Conformité
- Données sensibles chiffrées au repos (PostgreSQL + pgcrypto).
- Données en transit protégées par **TLS 1.3**.
- Respect du principe de **moindre privilège** (RBAC pour utilisateurs).
- Suppression définitive des documents selon les délais légaux.
- Audit RGPD trimestriel documenté.

---

## 🚀 Workflow DevOps
1. **Branches** : `main` (prod), `develop` (staging), `feature/*`.
2. **CI/CD** : GitHub Actions avec tests, lint, build et déploiement automatique.
3. **Revue de code** obligatoire par 2 pairs avant merge.
4. **Migration DB** validée et testée avant déploiement.
5. **Monitoring** : logs centralisés + alertes (Sentry, Prometheus).

---

## 📚 Documentation & Collaboration
- Chaque module doit avoir un **README.md**.
- API documentée avec **drf-spectacular** (OpenAPI 3).
- Frontend documenté avec **Storybook**.
- Décisions techniques consignées dans un **wiki interne**.
- Communication bienveillante et constructive dans les PR.