#!/usr/bin/env python3
"""
Script de revue de code approfondie avec suggestions d'amélioration.
Exécute une analyse complète et génère des rapports détaillés.
"""

import ast
import os
import sys
from typing import List, Dict, Any, Set
from pathlib import Path
import re


class DeepCodeReviewer:
    """Effectue une revue de code approfondie"""
    
    def __init__(self, root_dir: str = 'src'):
        self.root_dir = root_dir
        self.issues = []
        self.suggestions = []
        
    def analyze_all(self) -> None:
        """Analyse complète du code"""
        print("🔍 Analyse approfondie du code...")
        
        for filepath in self._get_python_files():
            print(f"  Analyse: {filepath}")
            self.analyze_file(filepath)
            
        self._print_report()
        
    def analyze_file(self, filepath: str) -> None:
        """Analyse un fichier Python"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=filepath)
                
            # Analyses multiples
            self._check_function_complexity(tree, filepath)
            self._check_class_design(tree, filepath)
            self._check_error_handling(tree, filepath)
            self._check_documentation(tree, filepath, content)
            self._check_naming_conventions(tree, filepath)
            self._check_code_duplication(content, filepath)
            self._check_performance_issues(tree, filepath)
            
        except Exception as e:
            self.issues.append({
                'file': filepath,
                'type': 'parse_error',
                'message': f"Erreur de parsing: {e}"
            })
            
    def _check_function_complexity(self, tree: ast.AST, filepath: str) -> None:
        """Vérifie la complexité des fonctions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                
                if complexity > 10:
                    self.issues.append({
                        'file': filepath,
                        'line': node.lineno,
                        'type': 'high_complexity',
                        'function': node.name,
                        'severity': 'high' if complexity > 15 else 'medium',
                        'message': f"Fonction '{node.name}' a une complexité de {complexity} (max recommandé: 10)",
                        'suggestion': "Décomposer en fonctions plus petites ou simplifier la logique"
                    })
                    
    def _check_class_design(self, tree: ast.AST, filepath: str) -> None:
        """Vérifie la conception des classes"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                attributes = self._count_attributes(node)
                
                # Trop de méthodes
                if len(methods) > 20:
                    self.issues.append({
                        'file': filepath,
                        'line': node.lineno,
                        'type': 'large_class',
                        'class': node.name,
                        'severity': 'medium',
                        'message': f"Classe '{node.name}' a {len(methods)} méthodes (max recommandé: 20)",
                        'suggestion': "Considérer diviser en plusieurs classes avec responsabilités uniques"
                    })
                    
                # Trop d'attributs
                if attributes > 10:
                    self.issues.append({
                        'file': filepath,
                        'line': node.lineno,
                        'type': 'too_many_attributes',
                        'class': node.name,
                        'severity': 'medium',
                        'message': f"Classe '{node.name}' a {attributes} attributs (max recommandé: 10)",
                        'suggestion': "Regrouper les attributs liés dans des sous-classes"
                    })
                    
    def _check_error_handling(self, tree: ast.AST, filepath: str) -> None:
        """Vérifie la gestion des erreurs"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Vérifier les except trop génériques
                for handler in node.handlers:
                    if handler.type is None or (
                        isinstance(handler.type, ast.Name) and handler.type.id == 'Exception'
                    ):
                        self.issues.append({
                            'file': filepath,
                            'line': handler.lineno,
                            'type': 'broad_exception',
                            'severity': 'medium',
                            'message': "Utilisation d'un 'except' trop générique",
                            'suggestion': "Capturer des exceptions spécifiques plutôt que 'Exception'"
                        })
                        
                # Vérifier les except pass (anti-pattern)
                for handler in node.handlers:
                    if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                        self.issues.append({
                            'file': filepath,
                            'line': handler.lineno,
                            'type': 'silent_exception',
                            'severity': 'high',
                            'message': "Exception silencieuse (except: pass)",
                            'suggestion': "Au minimum logger l'erreur, ou la re-lever si non gérable"
                        })
                        
    def _check_documentation(self, tree: ast.AST, filepath: str, content: str) -> None:
        """Vérifie la documentation"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                
                if not docstring:
                    # Ignorer les méthodes privées courtes
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('_'):
                        body_lines = node.end_lineno - node.lineno
                        if body_lines < 5:
                            continue
                            
                    self.issues.append({
                        'file': filepath,
                        'line': node.lineno,
                        'type': 'missing_docstring',
                        'name': node.name,
                        'severity': 'low',
                        'message': f"{'Classe' if isinstance(node, ast.ClassDef) else 'Fonction'} '{node.name}' sans docstring",
                        'suggestion': "Ajouter une docstring expliquant le comportement et les paramètres"
                    })
                    
    def _check_naming_conventions(self, tree: ast.AST, filepath: str) -> None:
        """Vérifie les conventions de nommage"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Les fonctions doivent être en snake_case
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
                    self.issues.append({
                        'file': filepath,
                        'line': node.lineno,
                        'type': 'naming_convention',
                        'severity': 'low',
                        'message': f"Fonction '{node.name}' ne respecte pas snake_case",
                        'suggestion': "Utiliser snake_case pour les noms de fonction"
                    })
                    
            elif isinstance(node, ast.ClassDef):
                # Les classes doivent être en PascalCase
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues.append({
                        'file': filepath,
                        'line': node.lineno,
                        'type': 'naming_convention',
                        'severity': 'low',
                        'message': f"Classe '{node.name}' ne respecte pas PascalCase",
                        'suggestion': "Utiliser PascalCase pour les noms de classe"
                    })
                    
    def _check_code_duplication(self, content: str, filepath: str) -> None:
        """Détecte la duplication de code"""
        lines = content.split('\n')
        
        # Chercher des blocs similaires (simpliste mais efficace)
        for i in range(len(lines) - 5):
            block = '\n'.join(lines[i:i+5])
            if len(block.strip()) < 50:  # Ignorer les petits blocs
                continue
                
            # Compter les occurrences
            count = content.count(block)
            if count > 1:
                self.suggestions.append({
                    'file': filepath,
                    'line': i + 1,
                    'type': 'code_duplication',
                    'message': f"Bloc de code dupliqué {count} fois",
                    'suggestion': "Extraire dans une fonction réutilisable"
                })
                break  # Une seule suggestion par fichier suffit
                
    def _check_performance_issues(self, tree: ast.AST, filepath: str) -> None:
        """Détecte les problèmes de performance potentiels"""
        for node in ast.walk(tree):
            # Boucles imbriquées
            if isinstance(node, ast.For):
                for inner in ast.walk(node):
                    if inner != node and isinstance(inner, ast.For):
                        self.issues.append({
                            'file': filepath,
                            'line': node.lineno,
                            'type': 'nested_loops',
                            'severity': 'medium',
                            'message': "Boucles imbriquées détectées - complexité O(n²) ou pire",
                            'suggestion': "Considérer des structures de données plus efficaces ou vectorisation"
                        })
                        break
                        
            # += dans une boucle (inefficace pour les strings)
            if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
                # Vérifier si on est dans une boucle
                parent = node
                in_loop = False
                # Note: Cette vérification nécessiterait un visitor plus sophistiqué
                
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calcule la complexité cyclomatique approximative"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
        
    def _count_attributes(self, node: ast.ClassDef) -> int:
        """Compte les attributs d'une classe"""
        attributes = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            attributes.add(target.attr)
                            
        return len(attributes)
        
    def _get_python_files(self) -> List[str]:
        """Récupère tous les fichiers Python"""
        files = []
        for root, dirs, filenames in os.walk(self.root_dir):
            # Ignorer __pycache__
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
                    
        return files
        
    def _print_report(self) -> None:
        """Affiche le rapport d'analyse"""
        print("\n" + "="*80)
        print("RAPPORT D'ANALYSE DE CODE")
        print("="*80)
        
        # Grouper par sévérité
        high = [i for i in self.issues if i.get('severity') == 'high']
        medium = [i for i in self.issues if i.get('severity') == 'medium']
        low = [i for i in self.issues if i.get('severity') == 'low']
        
        print(f"\n🚨 Problèmes critiques: {len(high)}")
        print(f"⚠️  Problèmes moyens: {len(medium)}")
        print(f"ℹ️  Problèmes mineurs: {len(low)}")
        print(f"💡 Suggestions: {len(self.suggestions)}")
        
        # Détails des problèmes critiques
        if high:
            print("\n" + "="*80)
            print("PROBLÈMES CRITIQUES À CORRIGER")
            print("="*80)
            for issue in high:
                print(f"\n📍 {issue['file']}:{issue.get('line', '?')}")
                print(f"   Type: {issue['type']}")
                print(f"   {issue['message']}")
                if 'suggestion' in issue:
                    print(f"   💡 {issue['suggestion']}")
                    
        # Résumé des suggestions
        if self.suggestions:
            print("\n" + "="*80)
            print("SUGGESTIONS D'AMÉLIORATION")
            print("="*80)
            for suggestion in self.suggestions[:10]:  # Limiter à 10
                print(f"\n📍 {suggestion['file']}:{suggestion.get('line', '?')}")
                print(f"   {suggestion['message']}")
                print(f"   💡 {suggestion['suggestion']}")
                
        # Score global
        total = len(high) + len(medium) + len(low)
        if total == 0:
            print("\n✅ Code de qualité exceptionnelle!")
        elif total < 10:
            print(f"\n✅ Bonne qualité de code ({total} problèmes mineurs)")
        elif total < 50:
            print(f"\n⚠️  Qualité acceptable ({total} problèmes à traiter)")
        else:
            print(f"\n🚨 Nécessite refactoring ({total} problèmes)")
            
        print("\n" + "="*80)


if __name__ == '__main__':
    reviewer = DeepCodeReviewer()
    reviewer.analyze_all()
    
    # Exit code selon la sévérité
    high = [i for i in reviewer.issues if i.get('severity') == 'high']
    sys.exit(1 if high else 0)
