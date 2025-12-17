#!/usr/bin/env python3
"""
Script d'analyse automatique de qualité de code.
Crée des issues GitHub pour les problèmes détectés.
"""

import json
import os
import sys
from typing import List, Dict, Any
from datetime import datetime
import subprocess

class QualityAnalyzer:
    """Analyse les rapports de qualité et crée des issues GitHub"""
    
    QUALITY_THRESHOLDS = {
        'pylint_score': 8.0,  # Score minimum acceptable
        'flake8_errors': 50,  # Nombre maximum d'erreurs
        'mypy_errors': 30,    # Nombre maximum d'erreurs de type
        'bandit_high': 0,     # Aucune vulnérabilité haute
        'bandit_medium': 5,   # Maximum 5 vulnérabilités moyennes
        'test_coverage': 70.0 # Couverture de tests minimale
    }
    
    def __init__(self):
        self.issues_to_create = []
        self.github_token = os.environ.get('GITHUB_TOKEN')
        
    def analyze_pylint(self, report_path: str) -> None:
        """Analyse le rapport Pylint"""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
                
            if not data:
                return
                
            # Calculer le score moyen
            score = 10.0 - (len(data) * 0.1)  # Approximation
            
            if score < self.QUALITY_THRESHOLDS['pylint_score']:
                # Grouper par type d'erreur
                error_groups = {}
                for item in data:
                    msg_type = item.get('message-id', 'unknown')
                    if msg_type not in error_groups:
                        error_groups[msg_type] = []
                    error_groups[msg_type].append(item)
                
                # Créer un issue pour chaque type d'erreur critique
                for msg_type, errors in error_groups.items():
                    if len(errors) >= 3:  # Au moins 3 occurrences
                        self._create_issue(
                            title=f"[Pylint] Améliorer: {msg_type}",
                            body=self._format_pylint_issue(msg_type, errors),
                            labels=['quality', 'pylint', 'automated']
                        )
                        
        except Exception as e:
            print(f"Erreur analyse Pylint: {e}")
            
    def analyze_bandit(self, report_path: str) -> None:
        """Analyse le rapport Bandit (sécurité)"""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
                
            results = data.get('results', [])
            
            high_severity = [r for r in results if r.get('issue_severity') == 'HIGH']
            medium_severity = [r for r in results if r.get('issue_severity') == 'MEDIUM']
            
            if len(high_severity) > self.QUALITY_THRESHOLDS['bandit_high']:
                self._create_issue(
                    title=f"🚨 [Sécurité] {len(high_severity)} vulnérabilités critiques détectées",
                    body=self._format_bandit_issue(high_severity, 'HIGH'),
                    labels=['security', 'critical', 'automated']
                )
                
            if len(medium_severity) > self.QUALITY_THRESHOLDS['bandit_medium']:
                self._create_issue(
                    title=f"⚠️ [Sécurité] {len(medium_severity)} vulnérabilités moyennes détectées",
                    body=self._format_bandit_issue(medium_severity, 'MEDIUM'),
                    labels=['security', 'medium', 'automated']
                )
                
        except Exception as e:
            print(f"Erreur analyse Bandit: {e}")
            
    def analyze_safety(self, report_path: str) -> None:
        """Analyse le rapport Safety (vulnérabilités dépendances)"""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
                
            vulnerabilities = data if isinstance(data, list) else []
            
            if vulnerabilities:
                self._create_issue(
                    title=f"📦 [Dépendances] {len(vulnerabilities)} vulnérabilités détectées",
                    body=self._format_safety_issue(vulnerabilities),
                    labels=['dependencies', 'security', 'automated']
                )
                
        except Exception as e:
            print(f"Erreur analyse Safety: {e}")
            
    def analyze_architecture(self) -> None:
        """Analyse l'architecture du code pour détecter les améliorations possibles"""
        improvements = []
        
        # Vérifier la complexité des fichiers
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    lines = self._count_lines(filepath)
                    
                    if lines > 500:
                        improvements.append(f"- `{filepath}` ({lines} lignes) devrait être refactorisé en modules plus petits")
                    
        # Vérifier les tests manquants
        src_files = set()
        test_files = set()
        
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    src_files.add(file.replace('.py', ''))
                    
        for root, dirs, files in os.walk('tests'):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.add(file.replace('test_', '').replace('.py', ''))
                    
        missing_tests = src_files - test_files
        if missing_tests:
            improvements.append(f"\n### Tests manquants\n")
            for module in missing_tests:
                improvements.append(f"- `test_{module}.py` n'existe pas")
                
        if improvements:
            self._create_issue(
                title="🏗️ [Architecture] Améliorations structurelles suggérées",
                body="\n".join(improvements),
                labels=['architecture', 'enhancement', 'automated']
            )
            
    def _format_pylint_issue(self, msg_type: str, errors: List[Dict]) -> str:
        """Formate un issue Pylint"""
        body = f"## Pylint: {msg_type}\n\n"
        body += f"**Occurrences:** {len(errors)}\n\n"
        body += "### Fichiers affectés:\n\n"
        
        for error in errors[:10]:  # Limiter à 10 exemples
            body += f"- `{error.get('path', 'unknown')}:{error.get('line', 0)}` - {error.get('message', '')}\n"
            
        if len(errors) > 10:
            body += f"\n... et {len(errors) - 10} autres\n"
            
        body += "\n### Action recommandée\n"
        body += "Refactoriser le code pour éliminer ces problèmes de qualité.\n"
        
        return body
        
    def _format_bandit_issue(self, results: List[Dict], severity: str) -> str:
        """Formate un issue Bandit"""
        body = f"## Vulnérabilités de sécurité ({severity})\n\n"
        body += f"**Nombre:** {len(results)}\n\n"
        
        for result in results[:10]:
            body += f"### {result.get('test_name', 'Unknown')}\n"
            body += f"- **Fichier:** `{result.get('filename', 'unknown')}:{result.get('line_number', 0)}`\n"
            body += f"- **Issue:** {result.get('issue_text', '')}\n"
            body += f"- **Confiance:** {result.get('issue_confidence', 'UNKNOWN')}\n\n"
            
        if len(results) > 10:
            body += f"... et {len(results) - 10} autres\n\n"
            
        body += "### Action urgente requise\n"
        body += "Ces vulnérabilités doivent être corrigées immédiatement.\n"
        
        return body
        
    def _format_safety_issue(self, vulnerabilities: List[Dict]) -> str:
        """Formate un issue Safety"""
        body = "## Vulnérabilités dans les dépendances\n\n"
        
        for vuln in vulnerabilities:
            package = vuln.get('package', 'unknown')
            installed = vuln.get('installed_version', 'unknown')
            affected = vuln.get('affected_versions', '')
            
            body += f"### {package}\n"
            body += f"- **Version installée:** {installed}\n"
            body += f"- **Versions affectées:** {affected}\n"
            body += f"- **Description:** {vuln.get('advisory', 'N/A')}\n\n"
            
        body += "### Action recommandée\n"
        body += "Mettre à jour les dépendances vers des versions sûres.\n"
        
        return body
        
    def _create_issue(self, title: str, body: str, labels: List[str]) -> None:
        """Ajoute un issue à créer"""
        self.issues_to_create.append({
            'title': title,
            'body': body,
            'labels': labels,
            'created_at': datetime.now().isoformat()
        })
        
    def _count_lines(self, filepath: str) -> int:
        """Compte les lignes de code (sans commentaires/lignes vides)"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                return len(code_lines)
        except:
            return 0
            
    def create_github_issues(self) -> None:
        """Crée les issues sur GitHub"""
        if not self.github_token:
            print("GITHUB_TOKEN non défini, simulation des issues:")
            for issue in self.issues_to_create:
                print(f"\n{'='*60}")
                print(f"Title: {issue['title']}")
                print(f"Labels: {', '.join(issue['labels'])}")
                print(f"Body:\n{issue['body']}")
            return
            
        # Créer les issues via GitHub CLI
        for issue in self.issues_to_create:
            try:
                cmd = [
                    'gh', 'issue', 'create',
                    '--title', issue['title'],
                    '--body', issue['body'],
                    '--label', ','.join(issue['labels'])
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Issue créé: {issue['title']}")
                else:
                    print(f"❌ Erreur création issue: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                
    def run(self) -> None:
        """Exécute l'analyse complète"""
        print("🔍 Analyse de la qualité du code...")
        
        # Analyser les rapports
        if os.path.exists('pylint-report.json'):
            self.analyze_pylint('pylint-report.json')
            
        if os.path.exists('bandit-report.json'):
            self.analyze_bandit('bandit-report.json')
            
        if os.path.exists('safety-report.json'):
            self.analyze_safety('safety-report.json')
            
        # Analyse architecturale
        self.analyze_architecture()
        
        # Créer les issues
        if self.issues_to_create:
            print(f"\n📝 {len(self.issues_to_create)} issues à créer")
            self.create_github_issues()
        else:
            print("\n✅ Aucun problème détecté - Excellente qualité!")


if __name__ == '__main__':
    analyzer = QualityAnalyzer()
    analyzer.run()
