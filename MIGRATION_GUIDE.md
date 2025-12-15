# Guide de Migration v1.x → v2.0

## 🎯 Principales Différences

### Architecture

| v1.x | v2.0 Professional |
|------|-------------------|
| Interface unique | Multi-interfaces simultanées |
| Configuration globale | Configuration par interface |
| Onglets simples | Panneau latéral + Onglets |
| Graphes uniquement | Dashboards avec 5 types de widgets |
| Pas d'énumérations | Support complet des énumérations |

### Interface Utilisateur

**v1.x** : Onglets horizontaux avec configuration, plot, sender, expert, triggers

**v2.0** : 
- **Panneau latéral** : Gestion des interfaces (dockable)
- **Onglet Messages** : Navigation hiérarchique des messages CAN
- **Onglet Dashboards** : Création de dashboards personnalisés
- **Onglet Envoyer** : Envoi de messages (conservé)
- **Onglet Déclencheurs** : Configuration des triggers (conservé)

## 🔄 Correspondances

### Connexion CAN

**v1.x** :
```
1. Onglet Configuration
2. Bouton "Connecter"
3. Dialogue de connexion
```

**v2.0** :
```
1. Panneau latéral "Interfaces CAN"
2. Cliquer "+ Interface"
3. Configurer l'interface
4. Bouton "Connecter" sur l'interface
```

### Chargement DBC

**v1.x** :
```
- Onglet Configuration
- Table de fichiers DBC
- Add/Remove/Reload
```

**v2.0** :
```
- Chaque interface a sa propre DBC
- Sélection via combo box
- Bouton 📁 pour parcourir
```

### Visualisation

**v1.x** :
```
- Onglet "Real-Time Plot"
- Sélecteur de signaux
- Graphes linéaires
```

**v2.0** :
```
- Onglet "Messages CAN" pour explorer
- Onglet "Dashboards" pour créer des vues
- 5 types de widgets disponibles
- Configurations sauvegardables
```

### Bus Load

**v1.x** :
```
- Onglet "Expert Mode"
- Table des messages
- Statistiques globales
```

**v2.0** :
```
- Directement dans le panneau de chaque interface
- Barre de progression colorée
- Statistiques par interface
```

## 📊 Migration des Workflows

### Workflow 1 : Monitoring Simple

**v1.x** :
1. Connecter une interface
2. Charger DBC
3. Sélectionner des signaux
4. Observer les graphes

**v2.0** :
1. Ajouter une interface (+ Interface)
2. Assigner une DBC à l'interface
3. Connecter l'interface
4. Explorer dans "Messages CAN" ou créer un Dashboard
5. Observer en temps réel

**Avantage** : Plusieurs interfaces peuvent être monitorées simultanément

### Workflow 2 : Analyse de Bus

**v1.x** :
1. Connecter
2. Aller dans Expert Mode
3. Observer le bus load

**v2.0** :
1. Ajouter une interface
2. Connecter
3. Bus load visible directement dans le panneau de l'interface
4. Pas besoin de changer d'onglet

**Avantage** : Monitoring permanent de toutes les interfaces

### Workflow 3 : Envoi de Messages

**v1.x & v2.0** : Identique
1. Onglet "Envoyer"
2. Configurer le message
3. Envoyer

**Note** : En v2.0, vous devez sélectionner l'interface cible

### Workflow 4 : Enregistrement

**v1.x** :
- Menu "Tools > Start Recording"

**v2.0** :
- Bouton ⏺️ dans la toolbar
- Ou menu "Outils > Démarrer enregistrement"

**Identique** : Format et fonctionnement inchangés

## 🎨 Nouvelles Fonctionnalités

### 1. Navigation Hiérarchique

**Nouveauté** : Explorez les messages par structure arborescente
```
📋 Messages CAN
  └─ VehicleSpeed (0x123)
      ├─ Speed (km/h)
      ├─ Valid (bool)
      └─ Counter (-)
```

- Cliquez sur un signal pour voir ses détails
- Recherche instantanée
- Valeurs en temps réel
- **Énumérations affichées automatiquement**

### 2. Système de Dashboards

**Totalement nouveau** : Créez des interfaces personnalisées

**Cas d'usage** :
- Dashboard "Diagnostic" avec états binaires et températures
- Dashboard "Performance" avec jauges de vitesse et RPM
- Dashboard "Confort" avec énumérations de modes

**Partage** :
- Exportez vos dashboards
- Importez des dashboards de collègues
- Créez des templates réutilisables

### 3. Support des Énumérations

**Nouveauté** : Les valeurs énumérées sont décodées automatiquement

Exemple DBC :
```
VAL_ 123 DriveMode 0 "ECO" 1 "COMFORT" 2 "SPORT" 3 "SPORT+";
```

**v1.x** : Affiche "2"
**v2.0** : Affiche "SPORT" avec "(valeur: 2)" en sous-texte

### 4. Multi-Interfaces

**Nouveauté majeure** : Plusieurs interfaces CAN simultanées

**Cas d'usage** :
- Gateway : Monitorer plusieurs bus CAN
- Test : Interface réelle + interface virtuelle
- Redondance : Deux interfaces sur le même bus
- Multi-véhicule : Plusieurs véhicules en même temps

Chaque interface :
- Nom personnalisé
- DBC indépendante
- Bus load séparé
- Connexion indépendante

## ⚙️ Configuration

### Fichiers Conservés

Ces fichiers de v1.x sont toujours utilisés :
- `config/default_config.json`
- `recordings/*.csv`
- Base de données DBC/SYM

### Nouveaux Fichiers

v2.0 ajoute :
- `dashboards/*.json` : Configurations de dashboards
- Pas de migration nécessaire des anciens fichiers

## 🚀 Recommandations

### Pour bien démarrer avec v2.0

1. **Explorez les Messages**
   - Connectez une interface
   - Allez dans "📋 Messages CAN"
   - Naviguez dans l'arbre des messages
   - Observez les valeurs en temps réel

2. **Créez un Dashboard**
   - Onglet "📊 Dashboards"
   - Cliquez "+ Nouveau"
   - Nommez votre dashboard
   - Ajoutez quelques widgets

3. **Importez l'Exemple**
   - Menu "Fichier > Importer Dashboard"
   - Sélectionnez `dashboards/example_vehicle.json`
   - Explorez le résultat

4. **Organisez vos Interfaces**
   - Donnez des noms explicites
   - Assignez les bonnes DBC
   - Gardez le panneau visible pour monitoring

### Astuces

- **Panneau Interfaces** : Peut être masqué/affiché via menu "Affichage"
- **Recherche** : Utilisez la recherche dans Messages CAN pour trouver rapidement
- **Dashboards** : Créez plusieurs dashboards pour différents contextes
- **Export** : Sauvegardez vos dashboards pour les réutiliser
- **Couleurs** : Les widgets s'adaptent automatiquement (vert/orange/rouge)

## 🐛 Problèmes Connus

### Compatibilité

- **SYM** : Toujours uniquement v6.0 (comme v1.x)
- **DBC** : Tous les formats supportés (comme v1.x)

### Limitations

- Les graphes de l'ancienne interface ne sont pas convertis en dashboards
- Il faut recréer vos vues dans le système de dashboards
- Les configurations de triggers sont conservées

## 📞 Support

Si vous rencontrez des difficultés :
1. Consultez `NEW_FEATURES.md` pour la documentation complète
2. Vérifiez `TROUBLESHOOTING.md` pour les problèmes courants
3. Consultez les logs dans le terminal

## 🎉 Profitez de v2.0!

La v2.0 représente une évolution majeure avec :
- ✅ Meilleure ergonomie
- ✅ Plus de flexibilité
- ✅ Design professionnel
- ✅ Fonctionnalités avancées
- ✅ Support des énumérations
- ✅ Dashboards personnalisables

Bon monitoring CAN ! 🚗💨
