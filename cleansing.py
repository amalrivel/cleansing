import pandas as pd
import re
from terbilang import Terbilang

t = Terbilang()

# abusive = pd.read_csv('dataset/abusive.csv', encoding='ISO-8859-1')
# filterAbusive = abusive["ABUSIVE"].tolist()

# alay = pd.read_csv('dataset/new_kamusalay.csv', encoding='ISO-8859-1', header=None)
# header = ['alay_word', 'replacement_word']
# alay.columns = header


class textCleansing:
    def __init__(self, filterAbusive, alay):
        self.filterAbusive = filterAbusive
        self.alay = alay

    def cleaning(self,teks):
        # Mengganti simbol %
        string = teks.replace('%', ' persen')

        # Mengganti simbol #
        string = re.sub(r'[#]+', 'hashtag ', string)

        # Menghapus karakter unicode
        string = re.sub(r'[^\x00-\x7F]+', '', string)

        # Menghilangkan enter dan tab
        string = re.sub(r'[\n\t]+', ' ', string)

        # Menghilangkan simbol, dan tanda baca
        string = re.sub(r'[^\w\d\s]+', '', string)

        # Mendeteksi dan mengganti angka menjadi kalimat bilangannya
        teks_split = string.split()
        kata_bersih = []
        for kata in teks_split:
            if kata.isdigit():
                t.parse(kata)
                kata_bersih.append(t.getresult())
                continue
            kata_bersih.append(kata)
        teks_bersih = " ".join(kata_bersih)

        # Menjadikan huruf kecil
        teks_bersih = str(teks_bersih).lower()
        return teks_bersih

    def cleansingAbusive(self, teks):
        teks_split = teks.split()
        kata_bersih = [
            kata for kata in teks_split if kata not in self.filterAbusive]
        teks_bersih = " ".join(kata_bersih)
        return teks_bersih

    def replace_words(self, teks):
        text_split = teks.split()
        for index, row in self.alay.iterrows():
            for i in range(len(text_split)):
                if text_split[i] == row['alay_word']:
                    text_split[i] = row['replacement_word']
        return ' '.join(text_split)
