"""
Metrics calculation and reporting for CodeDocGen.
"""
from typing import List, Dict, Any, TypedDict
from .models import Function

class LanguageStats(TypedDict):
    total: int
    documented: int

class MetricsCalculator:
    """Calculates and reports documentation coverage metrics."""

    def __init__(self):
        self.total_functions = 0
        self.documented_functions = 0
        self.files_processed = 0
        self.by_language: Dict[str, LanguageStats] = {}

    def update(self, functions: List[Function], language: str):
        """Update metrics with functions from a file."""
        self.files_processed += 1
        count = len(functions)
        doc_count = sum(1 for f in functions if f.brief_description or f.detailed_description)
        
        self.total_functions += count
        self.documented_functions += doc_count
        
        if language not in self.by_language:
            self.by_language[language] = {'total': 0, 'documented': 0}
        
        self.by_language[language]['total'] += count
        self.by_language[language]['documented'] += doc_count

    def calculate_coverage(self) -> float:
        """Calculate overall documentation coverage percentage."""
        if self.total_functions == 0:
            return 0.0
        return (self.documented_functions / self.total_functions) * 100

    def generate_report(self) -> str:
        """Generate a summary report."""
        coverage = self.calculate_coverage()
        report = [
            "\n=== Documentation Coverage Report ===",
            f"Files Processed: {self.files_processed}",
            f"Total Functions: {self.total_functions}",
            f"Documented Functions: {self.documented_functions}",
            f"Coverage: {coverage:.1f}%",
            "-------------------------------------",
            "Breakdown by Language:"
        ]
        
        for lang, stats in self.by_language.items():
            lang_coverage = (stats['documented'] / stats['total'] * 100) if stats['total'] > 0 else 0
            report.append(f"  {lang.capitalize()}: {stats['documented']}/{stats['total']} ({lang_coverage:.1f}%)")
            
        return "\n".join(report)
