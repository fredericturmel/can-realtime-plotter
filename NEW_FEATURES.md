# CAN Real-Time Plotter v2.0 - Professional Edition

## 🎨 Nouvelle Architecture Moderne

Cette version représente une refonte complète de l'application avec une architecture professionnelle et une ergonomie grandement améliorée.

## ✨ Nouvelles Fonctionnalités

### 1. Gestion Multi-Interfaces CAN

- **Panneau Latéral Dockable** : Gérez plusieurs interfaces CAN simultanément
- **Configuration Individuelle** : Chaque interface peut avoir :
  - Un nom personnalisé
  - Sa propre base de données DBC/SYM
  - Une connexion indépendante
  - Un monitoring du bus load en temps réel
- **Types Supportés** : PCAN, IXXAT, SocketCAN, Virtual

### 2. Navigateur de Messages Hiérarchique

- **Vue Arborescente** : Navigation claire par message CAN et signaux
- **Support des Énumérations** : Affichage automatique des valeurs d'énumération
- **Recherche Rapide** : Filtrage en temps réel des messages et signaux
- **Détails Complets** : 
  - Bits de départ et longueur
  - Facteur et offset
  - Type de données
  - Valeurs min/max
  - Descriptions et commentaires

### 3. Système de Dashboards Dynamiques

#### Types de Widgets Disponibles

1. **Jauge Circulaire** 🎯
   - Affichage visuel intuitif
   - Couleur adaptative selon la valeur
   - Min, max et unité configurables

2. **Affichage Numérique** 🔢
   - Grande lisibilité
   - Précision décimale configurable
   - Unités personnalisables

3. **État Binaire** 🔴🟢
   - Indicateur visuel ON/OFF
   - Labels personnalisables
   - Couleur automatique selon l'état

4. **Énumération** 📋
   - Affichage du nom de l'énumération
   - Valeur brute en complément
   - Support complet DBC/SYM

5. **Mini Graphe** 📈
   - Historique des valeurs
   - Axes et grille configurables
   - Limite de points personnalisable

#### Import/Export

- **Format JSON** : Configurations facilement éditables
- **Partage Simple** : Exportez et partagez vos dashboards
- **Réutilisation** : Importez des dashboards pré-configurés

### 4. Design Minimaliste et Professionnel

- **Palette Épurée** : Une seule couleur d'accent (bleu #58a6ff)
- **Contraste Optimal** : Fond sombre (#0d1117) pour réduire la fatigue oculaire
- **Hiérarchie Visuelle** : Espacement et bordures cohérents
- **Iconographie** : Emojis pour une reconnaissance rapide

## 📁 Structure des Fichiers

### Nouveaux Modules

```
src/gui/
├── modern_main_window.py      # Fenêtre principale refondée
├── interface_manager.py       # Gestion multi-interfaces
├── message_browser.py         # Navigateur de messages
├── dashboard_system.py        # Système de dashboards
└── (anciens modules conservés pour compatibilité)
```

### Dashboards

```
dashboards/
└── example_vehicle.json       # Exemple de dashboard véhicule
```

## 🚀 Utilisation

### Démarrage

```bash
python main.py
```

### Workflow Typique

1. **Ajouter une Interface**
   - Cliquez sur "+ Interface" dans la toolbar
   - Configurez le type et le canal
   - Assignez un nom personnalisé

2. **Charger une Base de Données**
   - Sélectionnez un fichier DBC/SYM pour l'interface
   - Le navigateur de messages se met à jour automatiquement

3. **Connecter l'Interface**
   - Cliquez sur "Connecter" dans le panneau de l'interface
   - Le monitoring du bus load démarre

4. **Explorer les Messages**
   - Onglet "📋 Messages CAN"
   - Navigation hiérarchique
   - Recherche par nom ou ID
   - Valeurs en temps réel avec énumérations

5. **Créer un Dashboard**
   - Onglet "📊 Dashboards"
   - Cliquez "+ Nouveau"
   - Ajoutez des widgets via "+ Ajouter Widget"
   - Configurez chaque widget (signal, position, taille)

6. **Exporter/Importer**
   - Bouton "💾 Exporter" sur un dashboard
   - Menu "Fichier > Importer Dashboard" pour charger

## 🎯 Exemples de Configuration

### Dashboard Exemple

Le fichier `dashboards/example_vehicle.json` contient un dashboard complet avec :
- 2 jauges (vitesse, régime moteur)
- 2 affichages numériques (température, carburant)
- 3 états binaires (contact, clignotants)
- 1 énumération (mode de conduite)
- 2 graphes (historiques)

### Import du Dashboard Exemple

1. Menu "Fichier > Importer Dashboard"
2. Sélectionnez `dashboards/example_vehicle.json`
3. Le dashboard est créé avec tous ses widgets

## 🔧 Configuration Avancée

### Personnalisation des Widgets

Les widgets peuvent être configurés via le JSON :

```json
{
  "type": "Jauge circulaire",
  "title": "Ma Jauge",
  "row": 0,
  "col": 0,
  "rowspan": 2,
  "colspan": 2,
  "config": {
    "min": 0,
    "max": 100,
    "unit": "km/h",
    "signal": "Message.Signal"
  }
}
```

### Signaux Supportés

Les signaux sont au format `MessageName.SignalName` et doivent correspondre à la base de données DBC/SYM chargée.

## 🎨 Thème et Style

### Palette de Couleurs

- **Arrière-plan** : #0d1117 (GitHub Dark)
- **Secondaire** : #161b22
- **Bordures** : #30363d
- **Texte** : #c9d1d9
- **Accent** : #58a6ff (bleu)
- **Succès** : #238636 (vert)
- **Danger** : #da3633 (rouge)
- **Avertissement** : #d29922 (orange)

### Composants

- **Boutons** : Bordures arrondies 6px, padding cohérent
- **Onglets** : Indicateur de sélection avec ligne bleue
- **Panneaux** : Cartes avec bordure #30363d
- **Widgets** : Arrondis 8px, fond #161b22

## 📊 Bus Load Monitoring

Chaque interface affiche en temps réel :
- **Pourcentage de charge** : Barre de progression colorée
- **Nombre de messages** : Compteur total
- **Erreurs** : Suivi des erreurs CAN

Couleurs adaptatives :
- 🟢 Vert < 50%
- 🟠 Orange 50-80%
- 🔴 Rouge > 80%

## 🔌 Gestion des Interfaces

### États Possibles

- **Déconnectée** : Bordure grise
- **Connectée** : Bordure verte, monitoring actif
- **Erreur** : Notification et déconnexion automatique

### Actions Disponibles

- **Renommer** : Éditez le nom directement dans le panneau
- **Changer de DBC** : Sélectionnez une autre base de données
- **Parcourir** : Bouton 📁 pour charger un nouveau fichier
- **Connecter/Déconnecter** : Toggle rapide

## 💡 Conseils d'Utilisation

1. **Organisation** : Créez un dashboard par cas d'usage (diagnostic, performance, état véhicule)
2. **Partage** : Exportez vos dashboards pour les réutiliser sur d'autres postes
3. **Monitoring** : Gardez le panneau interfaces visible pour surveiller le bus load
4. **Navigation** : Utilisez la recherche dans le navigateur de messages pour trouver rapidement un signal
5. **Énumérations** : Les valeurs d'énumération s'affichent automatiquement dans tous les widgets

## 🐛 Résolution de Problèmes

### Interface ne se connecte pas
- Vérifiez que le driver est installé
- Vérifiez le nom du canal (PCAN_USBBUS1, can0, etc.)
- Consultez les logs dans le terminal

### Signaux non décodés
- Assurez-vous que le DBC/SYM est chargé
- Vérifiez que l'ID CAN correspond à la base de données
- Format SYM : seule la version 6.0 est supportée

### Dashboard ne charge pas
- Vérifiez la syntaxe JSON
- Assurez-vous que les signaux existent dans la base de données
- Les noms de signaux sont sensibles à la casse

## 📝 Notes de Version

### v2.0 - Professional Edition

**Nouvelles Fonctionnalités**
- ✅ Gestion multi-interfaces CAN
- ✅ Navigateur hiérarchique de messages
- ✅ Support complet des énumérations
- ✅ Système de dashboards dynamiques
- ✅ 5 types de widgets (jauge, numérique, binaire, enum, graphe)
- ✅ Import/Export JSON des dashboards
- ✅ Design minimaliste épuré
- ✅ Panneau latéral dockable
- ✅ Bus load monitoring temps réel

**Améliorations**
- ⚡ Performance optimisée
- 🎨 Interface complètement repensée
- 📊 Meilleure visualisation des données
- 🔍 Recherche et filtrage améliorés
- 💾 Export/Import de configurations

## 🤝 Contribution

Pour contribuer ou signaler un bug, utilisez le système de tickets du projet.

## 📄 Licence

Voir le fichier LICENSE à la racine du projet.
