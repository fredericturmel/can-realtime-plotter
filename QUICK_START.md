# 🚀 Démarrage Rapide - CAN Real-Time Plotter v2.0

## ⚡ En 30 Secondes

```bash
# 1. Lancer l'application
python main.py

# 2. Ajouter une interface (bouton + Interface)

# 3. Connecter l'interface

# 4. Importer le dashboard exemple
Menu Fichier > Importer Dashboard > dashboards/example_vehicle.json
```

## 🎯 Premier Essai

### Option 1 : Avec Interface Virtuelle (Test)

1. **Ajouter Interface**
   - Cliquez `+ Interface` dans la toolbar
   - Nom : `Test Virtuel`
   - Type : `Virtual`
   - Canal : `vcan0`
   - Bitrate : `500000`
   - Cliquez `OK`

2. **Connecter**
   - Dans le panneau latéral, cliquez `Connecter`
   - L'interface passe en vert

3. **Explorer**
   - Onglet `📋 Messages CAN` : Voir les messages
   - Onglet `📊 Dashboards` : Créer un dashboard

### Option 2 : Avec Vraie Interface PCAN

1. **Ajouter Interface**
   - Cliquez `+ Interface`
   - Nom : `Mon PCAN`
   - Type : `PCAN`
   - Canal : `PCAN_USBBUS1` (ou votre canal)
   - Bitrate : `500000`

2. **Charger DBC**
   - Dans le panneau de l'interface
   - Cliquez `📁` à côté de "DBC/SYM"
   - Sélectionnez votre fichier .dbc

3. **Connecter**
   - Cliquez `Connecter`
   - Le bus load s'affiche en temps réel

4. **Visualiser**
   - Messages décodés dans l'onglet Messages
   - Créez un dashboard pour visualisation

## 📊 Créer Votre Premier Dashboard

### Méthode 1 : À partir de l'exemple

```bash
1. Menu "Fichier" > "Importer Dashboard"
2. Sélectionnez "dashboards/example_vehicle.json"
3. Le dashboard apparaît avec 10 widgets
4. Modifiez selon vos besoins
```

### Méthode 2 : De zéro

```bash
1. Onglet "📊 Dashboards"
2. Cliquez "+ Nouveau"
3. Nommez votre dashboard : "Mon Dashboard"
4. Cliquez "+ Ajouter Widget"
5. Choisissez le type (ex: Jauge circulaire)
6. Configurez :
   - Titre : "Vitesse"
   - Signal : "VehicleSpeed.Speed"
   - Position : Ligne 0, Colonne 0
   - Taille : 2x2
7. Cliquez OK
8. Répétez pour d'autres widgets
```

## 🎨 Types de Widgets - Quoi Utiliser?

| Widget | Quand l'utiliser | Exemple |
|--------|------------------|---------|
| 🎯 Jauge | Valeur avec min/max | Vitesse, RPM, Température |
| 🔢 Numérique | Valeur précise | Tension, Distance, Temps |
| 🔴 Binaire | État ON/OFF | Contact, Clignotant, Alarme |
| 📋 Énumération | Choix multiples | Mode conduite, État système |
| 📈 Graphe | Évolution temporelle | Historique température |

## 🔍 Navigation Rapide

### Raccourcis Clavier

- `Ctrl+O` : Importer dashboard
- `Ctrl+Q` : Quitter

### Organisation de l'Interface

```
┌─────────────────────────────────────────────┐
│ Menu │ Toolbar                              │
├──────────┬──────────────────────────────────┤
│ 🔌       │                                  │
│ Interface│  Onglets:                        │
│ Manager  │  - 📋 Messages CAN               │
│          │  - 📊 Dashboards                 │
│ (Dock)   │  - 📤 Envoyer                    │
│          │  - ⚡ Déclencheurs               │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

### Panneau Interfaces (Gauche)

**Masquer/Afficher** : Menu "Affichage" > "Panneau Interfaces"

**Contenu** :
- Liste des interfaces
- Bouton Connecter/Déconnecter
- Sélection DBC
- Bus Load en temps réel
- Statistiques

## 📝 Exemples de Signaux

Si vous avez chargé une DBC, les signaux sont au format :

```
MessageName.SignalName
```

Exemples :
- `VehicleSpeed.Speed`
- `EngineData.RPM`
- `Temperature.Coolant`
- `Status.IgnitionOn`

## 💡 Astuces

### 1. Bus Load
- 🟢 < 50% : OK
- 🟠 50-80% : Attention
- 🔴 > 80% : Critique

### 2. Recherche de Messages
- Tapez dans la barre de recherche de l'onglet Messages
- Filtrage instantané sur noms et IDs

### 3. Dashboards Multiples
- Créez plusieurs dashboards pour différents contextes
- Ex: "Diagnostic", "Performance", "Confort"
- Basculez via le sélecteur en haut

### 4. Export/Partage
- Exportez vos dashboards (💾 Exporter)
- Partagez les fichiers JSON
- Importez sur d'autres postes

## 🐛 Problèmes Courants

### Interface ne se connecte pas

```
✓ Vérifier le driver installé
✓ Vérifier le nom du canal
✓ Vérifier qu'aucune autre app n'utilise l'interface
✓ Consulter les logs dans le terminal
```

### Signaux non décodés

```
✓ DBC chargée pour cette interface ?
✓ ID CAN correspond à la DBC ?
✓ Format SYM : seule v6.0 supportée
```

### Dashboard vide après import

```
✓ DBC chargée ?
✓ Noms de signaux corrects dans le JSON ?
✓ Interface connectée ?
```

## 📚 En Savoir Plus

- **Documentation complète** : `NEW_FEATURES.md`
- **Migration v1→v2** : `MIGRATION_GUIDE.md`
- **Dashboards** : `dashboards/README.md`
- **Guide utilisateur** : `docs/USER_GUIDE.md`

## 🎉 C'est Parti !

```bash
python main.py
```

Amusez-vous bien avec la v2.0 ! 🚗💨
