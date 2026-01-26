# 🔐 GUIDE COMPLET - PERMISSIONS ENTRE AVOCATS

## 🎯 Principe de fonctionnement

### **RÈGLE D'OR : Cloisonnement par défaut**

```
┌──────────────────────────────────────────────────────────────┐
│  Un avocat NE VOIT PAS les dossiers des autres avocats      │
│  SAUF s'il est explicitement ajouté comme collaborateur      │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Matrice des permissions

### **1. Selon le rôle**

| Rôle | Dossiers visibles | Peut créer | Peut assigner collaborateurs |
|------|-------------------|------------|------------------------------|
| **Superuser** | Tous | ✅ | ✅ |
| **Admin (is_staff)** | Tous | ✅ | ✅ |
| **Avocat** | Ses dossiers + où il est collaborateur | ✅ | ✅ (ses dossiers) |
| **Notaire** | Ses dossiers + où il est collaborateur | ✅ | ✅ (ses dossiers) |
| **Conseil Juridique** | Ses dossiers + où il est collaborateur | ✅ | ✅ (ses dossiers) |
| **Stagiaire** | Où il est ajouté | ❌ | ❌ |
| **Assistant** | Où il est ajouté | ❌ | ❌ |
| **Secrétaire** | Où il est ajouté | ❌ | ❌ |

### **2. Selon le statut dans le dossier**

| Statut | Voir | Modifier | Supprimer | Ajouter collaborateurs | Ajouter documents |
|--------|------|----------|-----------|------------------------|-------------------|
| **Responsable** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Collaborateur (Avocat)** | ✅ | ✅* | ❌ | ❌ | ✅ |
| **Collaborateur (Stagiaire)** | ✅ | ❌ | ❌ | ❌ | ✅ |

*Selon permissions accordées

---

## 🚀 Cas d'usage pratiques

### **Cas 1 : Avocat A crée un dossier**

```python
# Maître Pierre Nze crée un dossier pour son client
POST /api/dossiers/
{
  "client": "client-uuid",
  "title": "Contentieux Mba c/ Nguema",
  "category": "CONTENTIEUX"
}

# Automatiquement :
# - Pierre devient "responsible"
# - Pierre obtient toutes les permissions sur ce dossier
# - Seul Pierre peut voir ce dossier
```

**Résultat :**
- ✅ Pierre voit le dossier
- ❌ Marie (autre avocate) ne voit PAS le dossier

---

### **Cas 2 : Avocat A ajoute Avocat B comme collaborateur**

```python
# Pierre veut que Marie l'aide sur ce dossier
POST /api/dossiers/{dossier_id}/assign-user/
{
  "user_id": "marie-uuid",
  "permissions": ["view", "change"]
}

# Marie est maintenant dans "assigned_users"
# Marie obtient les permissions Guardian
```

**Résultat :**
- ✅ Pierre voit le dossier (responsable)
- ✅ Marie voit le dossier (collaboratrice)
- ❌ André (autre avocat) ne voit PAS le dossier

---

### **Cas 3 : Avocat A ajoute un stagiaire**

```python
# Pierre ajoute un stagiaire pour l'assister
POST /api/dossiers/{dossier_id}/assign-user/
{
  "user_id": "stagiaire-uuid",
  "permissions": ["view"]  # Lecture seule
}
```

**Résultat :**
- ✅ Stagiaire peut voir le dossier
- ✅ Stagiaire peut voir les documents
- ✅ Stagiaire peut ajouter des documents
- ❌ Stagiaire ne peut PAS modifier le dossier
- ❌ Stagiaire ne peut PAS ajouter d'autres collaborateurs

---

### **Cas 4 : Retirer un collaborateur**

```python
# Pierre retire Marie du dossier
POST /api/dossiers/{dossier_id}/remove-user/
{
  "user_id": "marie-uuid"
}

# Marie perd immédiatement l'accès
```

**Résultat :**
- ❌ Marie ne voit plus le dossier dans sa liste
- ❌ Marie ne peut plus accéder aux documents

---

### **Cas 5 : Lister les collaborateurs**

```python
# Voir qui travaille sur un dossier
GET /api/dossiers/{dossier_id}/collaborateurs/

# Réponse :
{
  "responsable": {
    "id": "pierre-uuid",
    "name": "Pierre Nze Bekale",
    "role": "Avocat",
    "is_responsible": true,
    "permissions": ["view", "change", "delete", "assign"]
  },
  "collaborateurs": [
    {
      "id": "marie-uuid",
      "name": "Marie-Claire Ondo Ela",
      "role": "Avocat",
      "is_responsible": false,
      "permissions": ["view", "change"]
    },
    {
      "id": "stagiaire-uuid",
      "name": "Anne Ntoutoume",
      "role": "Stagiaire",
      "is_responsible": false,
      "permissions": ["view"]
    }
  ],
  "total_collaborateurs": 2
}
```

---

## 🔧 Implémentation Frontend

### **Composant : Assigner un collaborateur**

```vue
<template>
  <v-dialog v-model="dialog" max-width="600">
    <template v-slot:activator="{ props }">
      <v-btn
        v-if="canAssignUsers"
        color="indigo"
        v-bind="props"
      >
        <v-icon start>mdi-account-plus</v-icon>
        Ajouter un collaborateur
      </v-btn>
    </template>

    <v-card>
      <v-card-title>
        Ajouter un collaborateur
      </v-card-title>

      <v-card-text>
        <v-autocomplete
          v-model="selectedUser"
          :items="availableUsers"
          item-title="full_name"
          item-value="id"
          label="Sélectionner un utilisateur"
          prepend-inner-icon="mdi-account-search"
        >
          <template v-slot:item="{ item, props }">
            <v-list-item v-bind="props">
              <template v-slot:subtitle>
                {{ item.raw.role }} - {{ item.raw.email }}
              </template>
            </v-list-item>
          </template>
        </v-autocomplete>

        <v-select
          v-model="permissions"
          :items="permissionOptions"
          label="Permissions"
          multiple
          chips
        />
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn @click="dialog = false">Annuler</v-btn>
        <v-btn color="indigo" @click="assignUser">Ajouter</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDossierStore } from '@/stores/dossier'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  dossierId: { type: String, required: true },
  dossier: { type: Object, required: true }
})

const dossierStore = useDossierStore()
const authStore = useAuthStore()

const dialog = ref(false)
const selectedUser = ref(null)
const permissions = ref(['view'])
const availableUsers = ref([])

const permissionOptions = [
  { title: 'Consultation', value: 'view' },
  { title: 'Modification', value: 'change' }
]

// Vérifier si l'utilisateur courant peut assigner
const canAssignUsers = computed(() => {
  const currentUser = authStore.user
  return (
    currentUser.is_staff ||
    props.dossier.responsible === currentUser.id
  )
})

onMounted(async () => {
  // Charger les utilisateurs disponibles (avocats, stagiaires, etc.)
  const users = await dossierStore.fetchAvailableCollaborators()
  
  // Exclure ceux déjà assignés
  const assignedIds = props.dossier.assigned_users.map(u => u.id)
  availableUsers.value = users.filter(u => !assignedIds.includes(u.id))
})

async function assignUser() {
  await dossierStore.assignUser(props.dossierId, {
    user_id: selectedUser.value,
    permissions: permissions.value
  })
  
  dialog.value = false
  // Recharger le dossier
  await dossierStore.fetchDossier(props.dossierId)
}
</script>
```

---

## 📊 Tests de validation

### **Test 1 : Cloisonnement des dossiers**

```python
def test_avocat_ne_voit_pas_dossiers_autres_avocats(self):
    """Un avocat ne voit que ses propres dossiers"""
    avocat1 = User.objects.create_user(username='pierre', role='AVOCAT')
    avocat2 = User.objects.create_user(username='marie', role='AVOCAT')
    
    # Pierre crée un dossier
    dossier = Dossier.objects.create(
        responsible=avocat1,
        client=client,
        title="Dossier de Pierre"
    )
    
    # Marie essaie de lister les dossiers
    self.client.force_authenticate(avocat2)
    response = self.client.get('/api/dossiers/')
    
    # Marie ne doit PAS voir le dossier de Pierre
    assert response.status_code == 200
    assert len(response.data['results']) == 0
```

### **Test 2 : Collaborateur voit le dossier**

```python
def test_collaborateur_voit_dossier(self):
    """Un collaborateur assigné voit le dossier"""
    avocat1 = User.objects.create_user(username='pierre', role='AVOCAT')
    avocat2 = User.objects.create_user(username='marie', role='AVOCAT')
    
    dossier = Dossier.objects.create(responsible=avocat1, ...)
    
    # Ajouter Marie comme collaboratrice
    dossier.assigned_users.add(avocat2)
    assign_perm('view_dossier', avocat2, dossier)
    
    # Marie liste les dossiers
    self.client.force_authenticate(avocat2)
    response = self.client.get('/api/dossiers/')
    
    # Marie DOIT voir ce dossier
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == str(dossier.id)
```

### **Test 3 : Seul le responsable peut assigner**

```python
def test_seul_responsable_peut_assigner(self):
    """Seul le responsable peut ajouter des collaborateurs"""
    avocat1 = User.objects.create_user(username='pierre', role='AVOCAT')
    avocat2 = User.objects.create_user(username='marie', role='AVOCAT')
    avocat3 = User.objects.create_user(username='andre', role='AVOCAT')
    
    dossier = Dossier.objects.create(responsible=avocat1, ...)
    
    # Marie (non responsable) essaie d'ajouter André
    self.client.force_authenticate(avocat2)
    response = self.client.post(
        f'/api/dossiers/{dossier.id}/assign-user/',
        {'user_id': str(avocat3.id)}
    )
    
    # Doit échouer
    assert response.status_code == 403
```

---

## ✅ Checklist d'implémentation

- [ ] Ajouter les permissions dans `Dossier.Meta`
- [ ] Créer migration : `python manage.py makemigrations dossiers`
- [ ] Appliquer migration : `python manage.py migrate`
- [ ] Remplacer `get_queryset` dans `DossierViewSet`
- [ ] Ajouter actions `assign_user`, `remove_user`, `list_collaborateurs`
- [ ] Tester avec plusieurs avocats
- [ ] Implémenter composant Vue frontend
- [ ] Tester l'interface utilisateur

**Votre système de permissions est maintenant complet et conforme aux besoins d'un cabinet d'avocats, Maître Ahmed ! 🚀**