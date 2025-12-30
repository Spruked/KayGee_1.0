"""
Automatic Transparency Reporting
Daily self-generated audit report
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class SystemReporter:
    def __init__(self):
        self.reports_dir = Path("docs/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self):
        """Generate daily system report"""
        stats = self.get_philosopher_stats(days=7)
        invented = self.get_invented_terms()
        integrity = self.verify_integrity()
        
        md = f"""# Companion System Report — {datetime.now():%Y-%m-%d}

## Philosophical Activity (Last 7 Days)
{self.format_table(stats)}

## Emergent Concepts
{self.format_invented(invented)}

## System Integrity
- Trace Vault blocks: {integrity.get('trace_blocks', 0)}
- Chain valid: {'Yes' if integrity.get('valid', True) else 'NO'}
- A Priori checksum: {integrity.get('apriori_checksum', 'N/A')}

## Performance Metrics
- Average response time: {integrity.get('avg_response_ms', 'N/A')} ms
- Total decisions: {integrity.get('total_decisions', 0)}
- Ethical score average: {integrity.get('avg_ethical_score', 'N/A')}

## Recent High-Confidence Rules
{self.format_rules(integrity.get('rules', []))}
        """
        
        path = self.reports_dir / f"report_{datetime.now():%Y%m%d}.md"
        with open(path, "w") as f:
            f.write(md)
        
        print(f"[System Reporter] Generated report: {path}")
        return path
    
    def get_philosopher_stats(self, days: int = 7):
        """Get philosopher usage statistics"""
        # Mock implementation
        return {
            'kant': {'count': 45, 'avg_score': 0.82},
            'locke': {'count': 38, 'avg_score': 0.78},
            'spinoza': {'count': 22, 'avg_score': 0.75},
            'hume': {'count': 51, 'avg_score': 0.85}
        }
    
    def get_invented_terms(self):
        """Get invented terms summary"""
        # Mock implementation
        return [
            {'term': 'qua_digital_wellbeing', 'usage': 15, 'confidence': 0.88},
            {'term': 'blu_mindful_pause', 'usage': 12, 'confidence': 0.82}
        ]
    
    def verify_integrity(self):
        """Verify system integrity"""
        # Mock implementation
        return {
            'trace_blocks': 156,
            'valid': True,
            'apriori_checksum': 'a3f5b2c8d1e6f9...',
            'avg_response_ms': 45,
            'total_decisions': 156,
            'avg_ethical_score': 0.81,
            'rules': [
                'ethical(suggest_break) :- stress(high), time(work_hours).',
                'ethical(offer_tea) :- mood(calm), time(morning).'
            ]
        }
    
    def format_table(self, stats: Dict):
        """Format statistics as markdown table"""
        rows = []
        for philosopher, data in stats.items():
            rows.append(f"| {philosopher.capitalize()} | {data['count']} | {data['avg_score']:.2f} |")
        
        table = "| Philosopher | Decisions | Avg Score |\n"
        table += "|-------------|-----------|----------|\n"
        table += "\n".join(rows)
        return table
    
    def format_invented(self, invented: List[Dict]):
        """Format invented terms"""
        if not invented:
            return "No new invented terms this period."
        
        lines = []
        for term in invented:
            lines.append(f"- **{term['term']}**: Used {term['usage']} times (confidence: {term['confidence']:.2f})")
        return "\n".join(lines)
    
    def format_rules(self, rules: List[str]):
        """Format rules"""
        if not rules:
            return "No high-confidence rules yet."
        
        lines = []
        for rule in rules:
            lines.append(f"- `{rule}`")
        return "\n".join(lines)
