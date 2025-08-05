"""
Tests for Git integration functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess

from code_doc_gen.git_integration import GitIntegration


class TestGitIntegration:
    """Test cases for Git integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repo_path = Path("/tmp/test_repo")
        self.git_integration = GitIntegration(self.repo_path)
    
    @patch('subprocess.run')
    def test_is_git_repository_true(self, mock_run):
        """Test detecting a Git repository."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        git_integration = GitIntegration(self.repo_path)
        assert git_integration.is_git_repo is True
    
    @patch('subprocess.run')
    def test_is_git_repository_false(self, mock_run):
        """Test detecting a non-Git repository."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        git_integration = GitIntegration(self.repo_path)
        assert git_integration.is_git_repo is False
    
    @patch('subprocess.run')
    def test_is_git_repository_exception(self, mock_run):
        """Test handling exceptions when checking Git repository."""
        mock_run.side_effect = FileNotFoundError("git not found")
        
        git_integration = GitIntegration(self.repo_path)
        assert git_integration.is_git_repo is False
    
    @patch('subprocess.run')
    def test_get_changed_files_staged(self, mock_run):
        """Test getting staged changed files."""
        # Mock Git integration as a repository
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            # Mock staged files response
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "src/main.py\nsrc/utils.py\n"
            mock_run.return_value = mock_result
            
            # Mock file existence
            with patch.object(Path, 'exists', return_value=True):
                changed_files = git_integration.get_changed_files()
                assert len(changed_files) == 2
                assert any("main.py" in str(f) for f in changed_files)
                assert any("utils.py" in str(f) for f in changed_files)
    
    @patch('subprocess.run')
    def test_get_changed_files_unstaged(self, mock_run):
        """Test getting unstaged changed files."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            # Mock unstaged files response
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "src/test.py\n"
            mock_run.return_value = mock_result
            
            with patch.object(Path, 'exists', return_value=True):
                changed_files = git_integration.get_changed_files()
                assert len(changed_files) == 1
                assert any("test.py" in str(f) for f in changed_files)
    
    @patch('subprocess.run')
    def test_get_changed_files_untracked(self, mock_run):
        """Test getting untracked files."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            # Mock untracked files response
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "src/new_file.py\n"
            mock_run.return_value = mock_result
            
            with patch.object(Path, 'exists', return_value=True):
                changed_files = git_integration.get_changed_files(include_untracked=True)
                assert len(changed_files) == 1
                assert any("new_file.py" in str(f) for f in changed_files)
    
    @patch('subprocess.run')
    def test_get_changed_files_no_git_repo(self, mock_run):
        """Test getting changed files when not a Git repository."""
        git_integration = GitIntegration(self.repo_path)
        git_integration.is_git_repo = False
        
        changed_files = git_integration.get_changed_files()
        assert changed_files == []
    
    def test_filter_source_files(self):
        """Test filtering source files by extension."""
        files = [
            Path("/tmp/test.py"),
            Path("/tmp/test.cpp"),
            Path("/tmp/test.txt"),
            Path("/tmp/test.java")
        ]
        
        supported_extensions = ['.py', '.cpp', '.java']
        filtered_files = self.git_integration.filter_source_files(files, supported_extensions)
        
        assert len(filtered_files) == 3
        assert any(f.suffix == '.py' for f in filtered_files)
        assert any(f.suffix == '.cpp' for f in filtered_files)
        assert any(f.suffix == '.java' for f in filtered_files)
        assert not any(f.suffix == '.txt' for f in filtered_files)
    
    @patch('subprocess.run')
    def test_stage_file_success(self, mock_run):
        """Test successfully staging a file."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            file_path = Path("/tmp/test_repo/src/main.py")
            with patch.object(Path, 'relative_to', return_value=Path("src/main.py")):
                result = git_integration.stage_file(file_path)
                assert result is True
    
    @patch('subprocess.run')
    def test_stage_file_failure(self, mock_run):
        """Test failed file staging."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stderr = "Error staging file"
            mock_run.return_value = mock_result
            
            file_path = Path("/tmp/test_repo/src/main.py")
            with patch.object(Path, 'relative_to', return_value=Path("src/main.py")):
                result = git_integration.stage_file(file_path)
                assert result is False
    
    @patch('subprocess.run')
    def test_stage_file_no_git_repo(self, mock_run):
        """Test staging file when not a Git repository."""
        git_integration = GitIntegration(self.repo_path)
        git_integration.is_git_repo = False
        
        file_path = Path("/tmp/test_repo/src/main.py")
        result = git_integration.stage_file(file_path)
        assert result is False
    
    @patch('subprocess.run')
    def test_commit_changes_success(self, mock_run):
        """Test successful commit."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = git_integration.commit_changes("Test commit")
            assert result is True
    
    @patch('subprocess.run')
    def test_commit_changes_failure(self, mock_run):
        """Test failed commit."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stderr = "Error committing"
            mock_run.return_value = mock_result
            
            result = git_integration.commit_changes("Test commit")
            assert result is False
    
    @patch('subprocess.run')
    def test_commit_changes_no_git_repo(self, mock_run):
        """Test commit when not a Git repository."""
        git_integration = GitIntegration(self.repo_path)
        git_integration.is_git_repo = False
        
        result = git_integration.commit_changes("Test commit")
        assert result is False
    
    @patch('subprocess.run')
    def test_get_repo_status(self, mock_run):
        """Test getting repository status."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            # Mock branch response
            mock_branch_result = Mock()
            mock_branch_result.returncode = 0
            mock_branch_result.stdout = "main\n"
            
            # Mock status response
            mock_status_result = Mock()
            mock_status_result.returncode = 0
            mock_status_result.stdout = "M  src/main.py\n?? src/new_file.py\n"
            
            mock_run.side_effect = [mock_branch_result, mock_status_result]
            
            status = git_integration.get_repo_status()
            

            
            assert status['is_git_repo'] is True
            assert status['repo_path'] == str(self.repo_path)
            assert status['branch'] == 'main'
            assert status['has_changes'] is True
            assert 'src/main.py' in status['staged_files']  # M  means staged modified
            assert 'src/new_file.py' in status['untracked_files']
    
    @patch('subprocess.run')
    def test_get_repo_status_no_git_repo(self, mock_run):
        """Test getting status when not a Git repository."""
        git_integration = GitIntegration(self.repo_path)
        git_integration.is_git_repo = False
        
        status = git_integration.get_repo_status()
        
        assert status['is_git_repo'] is False
        assert status['repo_path'] == str(self.repo_path)
        assert status['branch'] is None
        assert status['has_changes'] is False
        assert status['staged_files'] == []
        assert status['unstaged_files'] == []
        assert status['untracked_files'] == []
    
    @patch('subprocess.run')
    def test_get_repo_status_exception(self, mock_run):
        """Test handling exceptions in status retrieval."""
        with patch.object(GitIntegration, '_is_git_repository', return_value=True):
            git_integration = GitIntegration(self.repo_path)
            
            # Mock both calls to fail
            mock_run.side_effect = Exception("Git error")
            
            status = git_integration.get_repo_status()
            
            assert status['is_git_repo'] is True
            assert status['repo_path'] == str(self.repo_path)
            assert status['branch'] is None
            assert status['has_changes'] is False 