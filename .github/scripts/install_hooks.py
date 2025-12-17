#!/usr/bin/env python3
"""
Script d'installation des hooks Git.
Exécuter: python .github/scripts/install_hooks.py
"""

import os
import shutil
import stat
from pathlib import Path


def install_hooks():
    """Installe les pre-commit hooks"""
    print("🔧 Installation des Git hooks...")
    
    # Chemins
    project_root = Path(__file__).parent.parent.parent
    hooks_source = project_root / '.github' / 'hooks'
    git_hooks_dir = project_root / '.git' / 'hooks'
    
    if not git_hooks_dir.exists():
        print("❌ Répertoire .git/hooks introuvable. Êtes-vous dans un dépôt Git?")
        return False
        
    # Copier le pre-commit hook
    source_hook = hooks_source / 'pre-commit'
    dest_hook = git_hooks_dir / 'pre-commit'
    
    if dest_hook.exists():
        print(f"⚠️  Hook existant trouvé: {dest_hook}")
        response = input("Écraser? (o/n): ")
        if response.lower() != 'o':
            print("❌ Installation annulée")
            return False
            
    try:
        shutil.copy(source_hook, dest_hook)
        
        # Rendre exécutable (Linux/Mac)
        if os.name != 'nt':
            st = os.stat(dest_hook)
            os.chmod(dest_hook, st.st_mode | stat.S_IEXEC)
            
        print(f"✅ Hook installé: {dest_hook}")
        
        # Installer les dépendances pour les hooks
        print("\n📦 Installation des dépendances de validation...")
        os.system('pip install black flake8 mypy bandit isort pytest -q')
        
        print("\n✅ Installation terminée!")
        print("\n💡 Le pre-commit hook va maintenant:")
        print("   - Vérifier le formatage du code (Black)")
        print("   - Vérifier le style (Flake8)")
        print("   - Vérifier les types (MyPy)")
        print("   - Vérifier la sécurité (Bandit)")
        print("   - Vérifier l'ordre des imports (isort)")
        print("   - Exécuter les tests unitaires")
        print("\n   Si une vérification échoue, le commit sera bloqué.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur installation: {e}")
        return False


if __name__ == '__main__':
    install_hooks()
