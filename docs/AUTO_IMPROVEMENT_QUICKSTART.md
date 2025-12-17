# CAN Real-Time Plotter - Auto-Improvement System 🤖

## Quick Start

### Installation
```bash
# Installer les hooks de validation locale
python .github/scripts/install_hooks.py

# Installer les dépendances de qualité
pip install black flake8 mypy bandit isort pytest pytest-cov safety pylint
```

### Configuration GitHub (optionnel)
Pour activer la revue IA automatique sur les Pull Requests:

**Option 1: OpenAI GPT-4 (payant ~$0.03/1K tokens)**
```
GitHub → Settings → Secrets → New secret
Name: OPENAI_API_KEY
Value: sk-...
```

**Option 2: Google Gemini (GRATUIT - 1500 req/jour)**
```
Name: GEMINI_API_KEY
Value: AIza...
```
Puis modifier `.github/workflows/ai-code-review.yml` pour utiliser Gemini au lieu d'OpenAI.

---

## Niveaux de Validation

### 🔒 Niveau 1: Pre-Commit (Local)
**Quand:** À chaque `git commit`

**Ce qui est vérifié:**
- ✅ Formatage du code (Black)
- ✅ Style PEP8 (Flake8, max complexité 10)
- ✅ Types (MyPy)
- ✅ Sécurité (Bandit)
- ✅ Ordre des imports (isort)
- ✅ Tests unitaires (pytest)

**Résultat:** Si UN SEUL check échoue → Commit **BLOQUÉ** ❌

### 🔄 Niveau 2: GitHub Actions (Continu)
**Quand:** 
- Push sur `main`/`develop`
- Pull Request
- Quotidiennement à 2h AM (proactif)

**Ce qui est fait:**
- Analyse complète de qualité (Pylint, Flake8, MyPy, Bandit, Safety)
- Tests avec couverture de code
- **Création automatique d'issues GitHub** pour problèmes détectés
- Génération de rapports téléchargeables

### 🤖 Niveau 3: AI Code Review (Pull Requests)
**Quand:** Sur chaque PR

**Ce qui est fait:**
- Analyse IA ultra-stricte avec GPT-4/Gemini
- Commentaires ligne par ligne
- Suggestions de corrections concrètes
- 7 catégories analysées (Sécurité, Bugs, Performance, Architecture, etc.)

---

## Utilisation Quotidienne

### Développement Normal
```bash
# 1. Modifier le code
vim src/mon_fichier.py

# 2. Tester localement (recommandé)
black src/ tests/
pytest

# 3. Commiter (hooks s'exécutent automatiquement)
git add .
git commit -m "feat: ma nouvelle feature"
# ✅ Si tout passe → Commit créé
# ❌ Si problème → Voir messages d'erreur et corriger

# 4. Push
git push origin ma-branche
```

### Si un Check Échoue
```bash
# Formatage
black src/ tests/

# Style
flake8 src/ tests/ --max-line-length=120

# Imports
isort src/ tests/

# Tests
pytest tests/ -v

# Puis réessayer
git commit -m "feat: ma feature"
```

### Contourner en Urgence (déconseillé)
```bash
git commit --no-verify -m "hotfix: urgence"
# ⚠️ Les checks s'exécuteront quand même sur GitHub!
```

---

## Revue Manuelle Approfondie

Lancer une analyse complète locale:
```bash
python .github/scripts/deep_code_review.py
```

Résultat:
```
🔍 Analyse approfondie du code...
  Analyse: src/gui/dashboard_system.py
  Analyse: src/gui/main_window.py
  ...

================================================================================
RAPPORT D'ANALYSE DE CODE
================================================================================

🚨 Problèmes critiques: 0
⚠️  Problèmes moyens: 3
ℹ️  Problèmes mineurs: 12
💡 Suggestions: 5

================================================================================
PROBLÈMES À CORRIGER
================================================================================

📍 src/gui/dashboard_system.py:234
   Type: high_complexity
   Fonction 'update_widget_data' a une complexité de 12 (max recommandé: 10)
   💡 Décomposer en fonctions plus petites ou simplifier la logique
```

---

## Monitoring de la Qualité

### Issues Automatiques
GitHub créera automatiquement des issues pour:
- 🚨 Vulnérabilités de sécurité (priorité critique)
- ⚠️ Complexité trop élevée (refactoring suggéré)
- 📦 Dépendances vulnérables (mise à jour requise)
- 📝 Tests manquants (couverture < 70%)
- 🏗️ Architecture (fichiers >500 lignes, classes >20 méthodes)

**Consulter:** GitHub → Issues → Filter by `label:automated`

### Rapports Téléchargeables
GitHub → Actions → Workflow run → Artifacts
- `quality-reports` (JSON/TXT des analyses)
- `coverage-report` (HTML interactif)

---

## Seuils de Qualité

Les seuils actuels (configurables dans `.github/scripts/analyze_and_create_issues.py`):

| Métrique | Seuil | Action si dépassé |
|----------|-------|-------------------|
| Score Pylint | < 8.0 | Issue créée |
| Erreurs Flake8 | > 50 | Issue créée |
| Erreurs MyPy | > 30 | Issue créée |
| Vulnérabilités critiques (Bandit) | > 0 | Issue CRITIQUE |
| Vulnérabilités moyennes (Bandit) | > 5 | Issue moyenne |
| Couverture tests | < 70% | Issue créée |
| Complexité fonction | > 10 | Warning, >15 Critique |
| Méthodes par classe | > 20 | Suggestion refactoring |
| Lignes par fichier | > 500 | Suggestion découpage |

---

## Workflow des Issues Automatiques

```
Code analysé quotidiennement à 2h AM
          ↓
Problèmes détectés (complexité, sécurité, etc.)
          ↓
Issues GitHub créées automatiquement
avec labels (automated, security, quality)
          ↓
Développeur assigné ou prend l'issue
          ↓
Correction + Tests
          ↓
PR créée → AI Review automatique
          ↓
Merge → Issue fermée automatiquement
```

---

## Personnalisation

### Changer les Seuils
Éditer `.github/scripts/analyze_and_create_issues.py`:
```python
QUALITY_THRESHOLDS = {
    'pylint_score': 9.0,      # Plus strict (était 8.0)
    'flake8_errors': 20,       # Plus strict (était 50)
    'test_coverage': 80.0      # Plus strict (était 70.0)
}
```

### Désactiver un Check
Éditer `.github/hooks/pre-commit`:
```python
checks = [
    # ("Formatage", check_code_formatting),  # Commenté = désactivé
    ("Style", check_code_style),
    ("Tests", run_unit_tests),
]
```

### Ajouter une Vérification Custom
Voir section "Personnalisation" dans `docs/AUTO_IMPROVEMENT_SYSTEM.md`

---

## Métriques de Succès

Après 1 mois d'utilisation, vous devriez voir:
- 📈 Score Pylint: 7.5 → 9.0+
- 📈 Couverture tests: 60% → 80%+
- 📉 Issues qualité: 50 → <10
- 📉 Vulnérabilités: X → 0
- 📉 Complexité moyenne: 12 → <7

**Le code s'améliore automatiquement! 🚀**

---

## Ressources

- 📖 **Documentation complète:** `docs/AUTO_IMPROVEMENT_SYSTEM.md`
- 🔧 **Scripts:** `.github/scripts/`
- ⚙️ **Workflows:** `.github/workflows/`
- 🎯 **Issues automatiques:** GitHub Issues avec `label:automated`

---

## Aide Rapide

**Problème:** "Pre-commit trop lent"
→ Désactiver temporairement certains checks ou corriger le code en amont

**Problème:** "Trop d'issues automatiques créées"
→ Ajuster les seuils dans `analyze_and_create_issues.py`

**Problème:** "AI Review ne fonctionne pas"
→ Vérifier que `OPENAI_API_KEY` ou `GEMINI_API_KEY` est configuré dans GitHub Secrets

**Problème:** "Check échoue sans raison apparente"
→ Consulter les logs détaillés dans GitHub Actions → Workflow run → Job logs

---

## 🎯 Objectif Final

> **"Code de qualité production avec zéro compromis"**

Le système garantit que chaque ligne de code est:
- ✅ Bien formatée
- ✅ Sans bug évident
- ✅ Sécurisée
- ✅ Performante
- ✅ Testée
- ✅ Documentée
- ✅ Maintenable

**Pendant que vous dormez, les IA veillent! 😴🤖**
