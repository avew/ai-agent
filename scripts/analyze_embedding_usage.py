#!/usr/bin/env python3
"""
Script untuk menganalisis penggunaan embedding OpenAI dari log files.
Berguna untuk memantau cost dan penggunaan API.
"""
import os
import re
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

class EmbeddingUsageAnalyzer:
    """Analyzer untuk menganalisis penggunaan embedding dari log files."""
    
    def __init__(self, log_file_path: str = "../logs/app.log"):
        self.log_file_path = log_file_path
        self.usage_pattern = re.compile(
            r'EMBEDDING_USAGE \| Operation: (\w+) \| '
            r'Model: ([\w-]+) \| '
            r'Tokens: ([\d,]+) \| '
            r'Requests: (\d+) \| '
            r'Time: ([\d.]+)s \| '
            r'Cost: \$([\d.]+) USD'
        )
        self.datetime_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
    
    def parse_log_file(self) -> List[Dict]:
        """Parse log file dan ekstrak data penggunaan embedding."""
        usage_data = []
        
        if not os.path.exists(self.log_file_path):
            print(f"❌ Log file tidak ditemukan: {self.log_file_path}")
            return usage_data
        
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Extract timestamp
                    datetime_match = self.datetime_pattern.search(line)
                    if not datetime_match:
                        continue
                    
                    timestamp_str = datetime_match.group(1)
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Extract embedding usage data
                    usage_match = self.usage_pattern.search(line)
                    if usage_match:
                        operation, model, tokens_str, requests, time_str, cost_str = usage_match.groups()
                        
                        # Clean token count (remove commas)
                        tokens = int(tokens_str.replace(',', ''))
                        
                        usage_data.append({
                            'timestamp': timestamp,
                            'operation': operation,
                            'model': model,
                            'tokens': tokens,
                            'requests': int(requests),
                            'time': float(time_str),
                            'cost': float(cost_str),
                            'line_num': line_num
                        })
                
                except Exception as e:
                    print(f"⚠️  Error parsing line {line_num}: {e}")
                    continue
        
        return usage_data
    
    def analyze_usage(self, usage_data: List[Dict], days: int = 30) -> Dict:
        """Analisis data penggunaan."""
        if not usage_data:
            return {}
        
        # Filter data berdasarkan rentang waktu
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_data = [item for item in usage_data if item['timestamp'] >= cutoff_date]
        
        if not filtered_data:
            return {}
        
        # Analisis umum
        total_cost = sum(item['cost'] for item in filtered_data)
        total_tokens = sum(item['tokens'] for item in filtered_data)
        total_requests = sum(item['requests'] for item in filtered_data)
        total_time = sum(item['time'] for item in filtered_data)
        
        # Analisis per model
        by_model = defaultdict(lambda: {'tokens': 0, 'requests': 0, 'cost': 0, 'time': 0, 'count': 0})
        for item in filtered_data:
            model = item['model']
            by_model[model]['tokens'] += item['tokens']
            by_model[model]['requests'] += item['requests']
            by_model[model]['cost'] += item['cost']
            by_model[model]['time'] += item['time']
            by_model[model]['count'] += 1
        
        # Analisis per operation
        by_operation = defaultdict(lambda: {'tokens': 0, 'requests': 0, 'cost': 0, 'time': 0, 'count': 0})
        for item in filtered_data:
            operation = item['operation']
            by_operation[operation]['tokens'] += item['tokens']
            by_operation[operation]['requests'] += item['requests']
            by_operation[operation]['cost'] += item['cost']
            by_operation[operation]['time'] += item['time']
            by_operation[operation]['count'] += 1
        
        # Analisis per hari
        by_day = defaultdict(lambda: {'tokens': 0, 'requests': 0, 'cost': 0, 'time': 0, 'count': 0})
        for item in filtered_data:
            day = item['timestamp'].date()
            by_day[day]['tokens'] += item['tokens']
            by_day[day]['requests'] += item['requests']
            by_day[day]['cost'] += item['cost']
            by_day[day]['time'] += item['time']
            by_day[day]['count'] += 1
        
        return {
            'summary': {
                'total_cost': total_cost,
                'total_tokens': total_tokens,
                'total_requests': total_requests,
                'total_time': total_time,
                'total_operations': len(filtered_data),
                'date_range': (min(item['timestamp'] for item in filtered_data).date(),
                              max(item['timestamp'] for item in filtered_data).date()),
                'days_analyzed': days
            },
            'by_model': dict(by_model),
            'by_operation': dict(by_operation),
            'by_day': dict(by_day)
        }
    
    def print_analysis(self, analysis: Dict):
        """Print analisis dalam format yang mudah dibaca."""
        if not analysis:
            print("❌ Tidak ada data embedding usage yang ditemukan.")
            return
        
        summary = analysis['summary']
        
        print("=" * 80)
        print("📊 ANALISIS PENGGUNAAN EMBEDDING OPENAI")
        print("=" * 80)
        
        # Summary
        print(f"\n📈 RINGKASAN ({summary['days_analyzed']} hari terakhir)")
        print(f"   📅 Periode: {summary['date_range'][0]} sampai {summary['date_range'][1]}")
        print(f"   💰 Total Cost: ${summary['total_cost']:.6f} USD")
        print(f"   🎯 Total Tokens: {summary['total_tokens']:,}")
        print(f"   📡 Total Requests: {summary['total_requests']:,}")
        print(f"   ⏱️  Total Time: {summary['total_time']:.2f} detik")
        print(f"   🔄 Total Operations: {summary['total_operations']:,}")
        
        if summary['total_tokens'] > 0:
            print(f"   📊 Rata-rata Cost per 1K tokens: ${(summary['total_cost'] / summary['total_tokens'] * 1000):.6f}")
        
        if summary['total_operations'] > 0:
            print(f"   📊 Rata-rata Tokens per Operation: {summary['total_tokens'] / summary['total_operations']:.1f}")
            print(f"   📊 Rata-rata Time per Operation: {summary['total_time'] / summary['total_operations']:.3f}s")
        
        # By Model
        print(f"\n🤖 PENGGUNAAN PER MODEL")
        for model, stats in analysis['by_model'].items():
            percentage = (stats['cost'] / summary['total_cost']) * 100 if summary['total_cost'] > 0 else 0
            print(f"   {model}:")
            print(f"      💰 Cost: ${stats['cost']:.6f} ({percentage:.1f}%)")
            print(f"      🎯 Tokens: {stats['tokens']:,}")
            print(f"      📡 Requests: {stats['requests']:,}")
            print(f"      🔄 Operations: {stats['count']:,}")
        
        # By Operation
        print(f"\n⚙️  PENGGUNAAN PER OPERATION")
        for operation, stats in analysis['by_operation'].items():
            percentage = (stats['cost'] / summary['total_cost']) * 100 if summary['total_cost'] > 0 else 0
            print(f"   {operation}:")
            print(f"      💰 Cost: ${stats['cost']:.6f} ({percentage:.1f}%)")
            print(f"      🎯 Tokens: {stats['tokens']:,}")
            print(f"      📡 Requests: {stats['requests']:,}")
            print(f"      🔄 Operations: {stats['count']:,}")
        
        # Top 10 days by cost
        print(f"\n📅 TOP 10 HARI DENGAN COST TERTINGGI")
        sorted_days = sorted(analysis['by_day'].items(), key=lambda x: x[1]['cost'], reverse=True)[:10]
        for i, (day, stats) in enumerate(sorted_days, 1):
            print(f"   {i:2d}. {day}: ${stats['cost']:.6f} | "
                  f"{stats['tokens']:,} tokens | "
                  f"{stats['requests']:,} requests | "
                  f"{stats['count']:,} operations")
        
        print("\n" + "=" * 80)
    
    def export_csv(self, usage_data: List[Dict], output_file: str = "embedding_usage.csv"):
        """Export data ke CSV file."""
        if not usage_data:
            print("❌ Tidak ada data untuk di-export.")
            return
        
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'operation', 'model', 'tokens', 'requests', 'time', 'cost']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in usage_data:
                writer.writerow({
                    'timestamp': item['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'operation': item['operation'],
                    'model': item['model'],
                    'tokens': item['tokens'],
                    'requests': item['requests'],
                    'time': item['time'],
                    'cost': item['cost']
                })
        
        print(f"✅ Data berhasil di-export ke: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Analisis penggunaan embedding OpenAI dari log files')
    parser.add_argument('--log-file', '-f', default='../logs/app.log', 
                       help='Path ke log file (default: ../logs/app.log)')
    parser.add_argument('--days', '-d', type=int, default=30,
                       help='Jumlah hari untuk dianalisis (default: 30)')
    parser.add_argument('--export-csv', '-e', action='store_true',
                       help='Export data ke CSV file')
    parser.add_argument('--output', '-o', default='../reports/embedding_usage.csv',
                       help='Output CSV file name (default: ../reports/embedding_usage.csv)')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = EmbeddingUsageAnalyzer(args.log_file)
    
    print(f"🔍 Menganalisis log file: {args.log_file}")
    
    # Parse log file
    usage_data = analyzer.parse_log_file()
    
    if not usage_data:
        print("❌ Tidak ditemukan data embedding usage dalam log file.")
        print("💡 Pastikan aplikasi sudah melakukan operasi embedding dan logging diaktifkan.")
        return
    
    print(f"✅ Ditemukan {len(usage_data)} record embedding usage")
    
    # Analyze data
    analysis = analyzer.analyze_usage(usage_data, args.days)
    
    # Print analysis
    analyzer.print_analysis(analysis)
    
    # Export to CSV if requested
    if args.export_csv:
        analyzer.export_csv(usage_data, args.output)

if __name__ == "__main__":
    main()
