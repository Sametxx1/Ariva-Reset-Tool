import requests
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor

def get_csrf_token():
    """Instagram'dan CSRF token alan fonksiyon"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        response = requests.get('https://www.instagram.com/', headers=headers)
        
        # CSRF token'ı bulmak için regex kullanımı
        csrf_token = re.search(r'\"csrf_token\":\"(.*?)\"', response.text)
        
        if csrf_token:
            return csrf_token.group(1)
        else:
            return None
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return None

def save_tokens_to_file(tokens, filename="csrf.txt"):
    """Bulunan token'ları dosyaya kaydetme fonksiyonu"""
    with open(filename, 'w') as file:
        for token in tokens:
            file.write(f"{token}\n")
    print(f"{len(tokens)} adet token {filename} dosyasına kaydedildi.")

def collect_tokens(count):
    """Belirtilen sayıda token toplama fonksiyonu"""
    tokens = []
    success_count = 0
    attempt_count = 0
    max_attempts = count * 2  # Maksimum deneme sayısı
    
    print(f"{count} adet CSRF token toplanıyor...")
    
    while success_count < count and attempt_count < max_attempts:
        token = get_csrf_token()
        attempt_count += 1
        
        if token:
            # Daha önce bulunan token'ları tekrar eklemeyelim
            if token not in tokens:
                tokens.append(token)
                success_count += 1
                print(f"Token {success_count}/{count} bulundu: {token[:10]}...")
            
            # Instagram'ın rate limit'inden kaçınmak için bekletme
            sleep_time = random.uniform(1.5, 3.0)
            time.sleep(sleep_time)
        else:
            print("Token bulunamadı, tekrar deneniyor...")
            time.sleep(5)  # Hata durumunda daha uzun bekleme
    
    return tokens

def collect_tokens_parallel(count, max_workers=5):
    """Paralel şekilde token toplama fonksiyonu"""
    tokens = []
    workers = min(max_workers, count)  # Worker sayısı token sayısından fazla olmasın
    tokens_per_worker = count // workers + (1 if count % workers else 0)
    
    def worker_task(worker_count):
        worker_tokens = []
        for _ in range(worker_count):
            token = get_csrf_token()
            if token:
                worker_tokens.append(token)
                # Rate limit'ten kaçınmak için bekletme
                time.sleep(random.uniform(1.5, 3.0))
        return worker_tokens
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker_task, tokens_per_worker) for _ in range(workers)]
        for future in futures:
            worker_result = future.result()
            tokens.extend(worker_result)
    
    # Fazla token varsa kırp
    return tokens[:count]

def main():
    try:
        token_count = int(input("Kaç adet CSRF token toplamak istiyorsunuz? "))
        
        if token_count <= 0:
            print("Geçerli bir sayı giriniz.")
            return
        
        # Paralel çalışma için seçenek sun
        use_parallel = input("Paralel çalışma modunu kullanmak ister misiniz? (e/h): ").lower() == 'e'
        
        start_time = time.time()
        
        if use_parallel and token_count > 5:
            tokens = collect_tokens_parallel(token_count)
        else:
            tokens = collect_tokens(token_count)
        
        end_time = time.time()
        
        if tokens:
            save_tokens_to_file(tokens)
            print(f"İşlem tamamlandı! Geçen süre: {end_time - start_time:.2f} saniye")
        else:
            print("Token toplanamadı.")
            
    except ValueError:
        print("Lütfen geçerli bir sayı giriniz.")
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")

if __name__ == "__main__":
    main()
