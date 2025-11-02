import csv

def dosya_oku(dosya_adi):
    with open(dosya_adi, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def ortalama_hesapla(veri, sutun):
    toplam = 0
    for satir in veri:
        toplam += float(satir[sutun])
    return toplam / len(veri)

def en_yuksek_bul(veri, sutun):
    return max(veri, key=lambda x: float(x[sutun]))

def en_dusuk_bul(veri, sutun):
    return min(veri, key=lambda x: float(x[sutun]))

def filtrele(veri, sutun, alt_limit):
    return [satir for satir in veri if float(satir[sutun]) > alt_limit]

def menu():
    print("\n--- Veri Analiz Uygulaması ---")
    print("1. Ortalama maaş")
    print("2. En yüksek maaş")
    print("3. En düşük maaş")
    print("4. Belirli maaşın üzerindekileri listele")
    print("5. Çıkış")

def main():
    veri = dosya_oku("veri.csv")

    while True:
        menu()
        secim = input("Seçiminiz: ")

        if secim == "1":
            print(f"Ortalama maaş: {ortalama_hesapla(veri, 'maaş'):.2f} ₺")

        elif secim == "2":
            en_yuksek = en_yuksek_bul(veri, 'maaş')
            print(f"En yüksek maaş: {en_yuksek['isim']} ({en_yuksek['maaş']} ₺)")

        elif secim == "3":
            en_dusuk = en_dusuk_bul(veri, 'maaş')
            print(f"En düşük maaş: {en_dusuk['isim']} ({en_dusuk['maaş']} ₺)")

        elif secim == "4":
            limit = float(input("Alt limit maaş değeri girin: "))
            sonuc = filtrele(veri, 'maaş', limit)
            if sonuc:
                print("Bu maaşın üzerindekiler:")
                for kisi in sonuc:
                    print(f"{kisi['isim']} - {kisi['maaş']} ₺")
            else:
                print("Bu değerin üzerinde maaş alan yok.")

        elif secim == "5":
            print("Program sonlandırıldı.")
            break
        else:
            print("Geçersiz seçim, tekrar deneyin!")

if __name__ == "__main__":
    main()
