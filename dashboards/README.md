# Dashboards

Ce dossier contient les configurations de dashboards exportées au format JSON.

## 📊 Dashboards Disponibles

### example_vehicle.json
Dashboard complet pour monitoring véhicule avec :
- Jauges pour vitesse et régime moteur
- Affichages numériques pour température et carburant
- États binaires pour contact et clignotants
- Énumération pour le mode de conduite
- Graphes d'historique

## 🔧 Structure d'un Dashboard

```json
{
  "name": "Nom du Dashboard",
  "widgets": [
    {
      "type": "Type de widget",
      "title": "Titre affiché",
      "row": 0,
      "col": 0,
      "rowspan": 1,
      "colspan": 1,
      "config": {
        // Configuration spécifique au widget
      }
    }
  ]
}
```

## 📝 Types de Widgets

### 1. Jauge circulaire
```json
{
  "type": "Jauge circulaire",
  "config": {
    "min": 0,
    "max": 100,
    "unit": "km/h",
    "signal": "Message.Signal"
  }
}
```

### 2. Affichage numérique
```json
{
  "type": "Affichage numérique",
  "config": {
    "unit": "°C",
    "decimals": 2,
    "signal": "Message.Signal"
  }
}
```

### 3. État binaire
```json
{
  "type": "État binaire",
  "config": {
    "true_label": "ON",
    "false_label": "OFF",
    "signal": "Message.Signal"
  }
}
```

### 4. Énumération
```json
{
  "type": "Énumération",
  "config": {
    "signal": "Message.Signal",
    "enum_values": {
      "0": "Valeur 0",
      "1": "Valeur 1"
    }
  }
}
```

### 5. Mini graphe
```json
{
  "type": "Mini graphe",
  "config": {
    "unit": "km/h",
    "max_points": 200,
    "signal": "Message.Signal"
  }
}
```

## 🎯 Positionnement

- **row** : Ligne de départ (0-indexé)
- **col** : Colonne de départ (0-indexé)
- **rowspan** : Nombre de lignes occupées
- **colspan** : Nombre de colonnes occupées

## 💡 Conseils

1. **Organisation** : Groupez les widgets par fonction
2. **Taille** : Les jauges sont plus lisibles avec rowspan=2, colspan=2
3. **Graphes** : Utilisez rowspan=2 pour une meilleure visibilité
4. **Signaux** : Format `MessageName.SignalName`
5. **Couleurs** : Les widgets s'adaptent automatiquement au thème

## 🚀 Import/Export

### Exporter un Dashboard
1. Créez votre dashboard dans l'application
2. Cliquez sur "💾 Exporter"
3. Sauvegardez le fichier dans ce dossier

### Importer un Dashboard
1. Menu "Fichier > Importer Dashboard"
2. Sélectionnez le fichier JSON
3. Le dashboard est chargé avec tous ses widgets
