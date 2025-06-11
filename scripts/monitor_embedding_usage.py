#!/usr/bin/env python3
"""
Real-time monitor untuk penggunaan embedding OpenAI.
Script ini akan memantau log file secara real-time dan menampilkan penggunaan embedding.
"""
import os
import re
import time
import signal
import sys
from datetime import datetime
from typing import Dict, Optional

class EmbeddingMonitor:
    """Real-time monitor untuk penggunaan embedding."""
    
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
        self.running = True
        self.total_cost = 0.0
        self.total_tokens = 0
        self.total_requests = 0
        self.session_start = datetime.now()
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signal."""
        print(f"\n\n📊 SESSION SUMMARY")
        print(f"   ⏱️  Duration: {datetime.now() - self.session_start}")
        print(f"   💰 Total Cost: ${self.total_cost:.6f} USD")
        print(f"   🎯 Total Tokens: {self.total_tokens:,}")
        print(f"   📡 Total Requests: {self.total_requests:,}")
        print(f"\n👋 Monitoring stopped. Goodbye!")
        sys.exit(0)
    
    def parse_embedding_line(self, line: str) -> Optional[Dict]:
        """Parse line untuk ekstrak data embedding usage."""
        try:
            # Extract timestamp
            datetime_match = self.datetime_pattern.search(line)
            if not datetime_match:
                return None
            
            timestamp_str = datetime_match.group(1)
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            # Extract embedding usage data
            usage_match = self.usage_pattern.search(line)
            if not usage_match:
                return None
            
            operation, model, tokens_str, requests, time_str, cost_str = usage_match.groups()
            
            # Clean token count (remove commas)
            tokens = int(tokens_str.replace(',', ''))
            
            return {
                'timestamp': timestamp,
                'operation': operation,
                'model': model,
                'tokens': tokens,
                'requests': int(requests),
                'time': float(time_str),
                'cost': float(cost_str)
            }
        
        except Exception:
            return None
    
    def format_usage_display(self, usage: Dict) -> str:
        """Format usage data untuk display."""
        timestamp = usage['timestamp'].strftime('%H:%M:%S')
        return (
            f"⏰ {timestamp} | "
            f"🔄 {usage['operation']:12} | "
            f"🤖 {usage['model']:20} | "
            f"🎯 {usage['tokens']:>8,} tokens | "
            f"📡 {usage['requests']:>3} req | "
            f"⏱️  {usage['time']:>6.3f}s | "
            f"💰 ${usage['cost']:>9.6f}"
        )
    
    def monitor(self):
        """Monitor log file secara real-time."""
        print("🔍 EMBEDDING USAGE MONITOR")
        print("=" * 120)
        print("⏰ Time     | 🔄 Operation    | 🤖 Model               | 🎯   Tokens | 📡 Req | ⏱️   Time | 💰      Cost")
        print("-" * 120)
        
        if not os.path.exists(self.log_file_path):
            print(f"❌ Log file tidak ditemukan: {self.log_file_path}")
            print("💡 Pastikan aplikasi berjalan dan logging diaktifkan.")
            return
        
        # Start monitoring from end of file
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while self.running:
                line = f.readline()
                
                if line:
                    usage = self.parse_embedding_line(line.strip())
                    if usage:
                        # Update totals
                        self.total_cost += usage['cost']
                        self.total_tokens += usage['tokens']
                        self.total_requests += usage['requests']
                        
                        # Display usage
                        print(self.format_usage_display(usage))
                        
                        # Display running totals every 10 operations
                        if self.total_requests % 10 == 0:
                            duration = datetime.now() - self.session_start
                            print(f"📊 Session Total: ${self.total_cost:.6f} | "
                                  f"{self.total_tokens:,} tokens | "
                                  f"{self.total_requests:,} requests | "
                                  f"Duration: {duration}")
                            print("-" * 120)
                else:
                    # No new data, wait a bit
                    time.sleep(0.5)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time monitor untuk penggunaan embedding OpenAI')
    parser.add_argument('--log-file', '-f', default='../logs/app.log', 
                       help='Path ke log file (default: ../logs/app.log)')
    
    args = parser.parse_args()
    
    monitor = EmbeddingMonitor(args.log_file)
    
    print(f"🚀 Starting embedding monitor...")
    print(f"📁 Monitoring: {args.log_file}")
    print(f"⏹️  Press Ctrl+C to stop\n")
    
    try:
        monitor.monitor()
    except KeyboardInterrupt:
        pass  # Handled by signal handler

if __name__ == "__main__":
    main()
