"""
Git integration for CodeDocGen.

Provides Git operations for detecting changed files and auto-committing
generated documentation.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import subprocess
import os


class GitIntegration:
    """Git integration for repository operations."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize Git integration.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger(__name__)
        
        # Check if this is a Git repository
        self.is_git_repo = self._is_git_repository()
        
        if not self.is_git_repo:
            self.logger.warning(f"Not a Git repository: {repo_path}")
    
    def _is_git_repository(self) -> bool:
        """
        Check if the path is a Git repository.
        
        Returns:
            True if it's a Git repository
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def get_changed_files(self, include_untracked: bool = True) -> List[Path]:
        """
        Get list of changed files in the repository.
        
        Args:
            include_untracked: Whether to include untracked files
            
        Returns:
            List of changed file paths
        """
        if not self.is_git_repo:
            return []
        
        changed_files = []
        
        try:
            # Get modified and staged files
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--cached'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        file_path = self.repo_path / line.strip()
                        if file_path.exists():
                            changed_files.append(file_path)
            
            # Get unstaged changes
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        file_path = self.repo_path / line.strip()
                        if file_path.exists() and file_path not in changed_files:
                            changed_files.append(file_path)
            
            # Include untracked files if requested
            if include_untracked:
                result = subprocess.run(
                    ['git', 'ls-files', '--others', '--exclude-standard'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            file_path = self.repo_path / line.strip()
                            if file_path.exists() and file_path not in changed_files:
                                changed_files.append(file_path)
            
            self.logger.info(f"Found {len(changed_files)} changed files")
            
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.logger.error(f"Error getting changed files: {e}")
        
        return changed_files
    
    def filter_source_files(self, files: List[Path], supported_extensions: List[str]) -> List[Path]:
        """
        Filter files to only include source files with supported extensions.
        
        Args:
            files: List of file paths
            supported_extensions: List of supported file extensions
            
        Returns:
            Filtered list of source files
        """
        source_files = []
        
        for file_path in files:
            if file_path.suffix.lower() in supported_extensions:
                source_files.append(file_path)
        
        return source_files
    
    def stage_file(self, file_path: Path) -> bool:
        """
        Stage a file for commit.
        
        Args:
            file_path: Path to the file to stage
            
        Returns:
            True if successful
        """
        if not self.is_git_repo:
            return False
        
        try:
            # Convert to relative path from repo root
            rel_path = file_path.relative_to(self.repo_path)
            
            result = subprocess.run(
                ['git', 'add', str(rel_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"Staged {file_path}")
                return True
            else:
                self.logger.error(f"Failed to stage {file_path}: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.logger.error(f"Error staging {file_path}: {e}")
            return False
    
    def commit_changes(self, message: str = "Auto-generated documentation") -> bool:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            
        Returns:
            True if successful
        """
        if not self.is_git_repo:
            return False
        
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"Committed changes: {message}")
                return True
            else:
                self.logger.error(f"Failed to commit: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.logger.error(f"Error committing changes: {e}")
            return False
    
    def get_repo_status(self) -> Dict[str, Any]:
        """
        Get repository status information.
        
        Returns:
            Dictionary with repository status
        """
        status = {
            'is_git_repo': self.is_git_repo,
            'repo_path': str(self.repo_path),
            'branch': None,
            'has_changes': False,
            'staged_files': [],
            'unstaged_files': [],
            'untracked_files': []
        }
        
        if not self.is_git_repo:
            return status
        
        try:
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                status['branch'] = result.stdout.strip()
            
            # Get status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                has_changes = False
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        has_changes = True
                        status_code = line[:2]
                        file_path = line[3:]
                        

                        
                        if status_code in ['A ', 'M ']:  # Staged files
                            status['staged_files'].append(file_path)
                        elif status_code in [' M', ' D']:  # Unstaged files
                            status['unstaged_files'].append(file_path)
                        elif status_code == '??':  # Untracked files
                            status['untracked_files'].append(file_path)
                
                status['has_changes'] = has_changes
            
        except Exception as e:
            self.logger.error(f"Error getting repository status: {e}")
        
        return status 