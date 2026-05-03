-ReseptiApp

Flaskilla ja SQLitellä toteutettu verkkosovellus, jonka avulla käyttäjät voivat
lisätä, selata ja arvioida ruokareseptejä.

-Sovelluksen toiminnot

- Etusivu näyttää kaikki lisätyt reseptit sekä sovelluksen tilastot
  (reseptien, käyttäjien ja kommenttien määrät). **Etusivun voi nähdä myös
  ilman kirjautumista.**
- Käyttäjä voi rekisteröityä ja kirjautua sisään. Salasanat tallennetaan
  hashattuna (werkzeug).
- Kirjautunut käyttäjä voi lisätä uuden reseptin, jolle annetaan nimi,
  ainekset, ohjeet sekä yksi tai useampi luokittelu.
- Luokittelut ovat valmiiksi tietokannassa. Jokaiselle reseptille voi valita
  arvoja kategorioista **Tyyppi**, **Keittiö** ja **Ruokavalio**.
- Käyttäjä voi muokata ja poistaa vain omia reseptejään.
- Käyttäjä voi jättää **toisen käyttäjän reseptiin** kommentin ja tähtiarvion
  (1–5). Kommentit näkyvät reseptin sivulla, ja reseptin keskiarvo lasketaan
  arvioista.
- Käyttäjäsivu näyttää käyttäjän lisäämät reseptit sekä tilastot: kuinka monta
  reseptiä ja kommenttia käyttäjä on lisännyt, kuinka monta kommenttia hänen
  resepteihinsä on jätetty ja mikä on reseptien keskimääräinen arvio.
- Hakutoiminto hakee reseptin nimen tai aineksen perusteella.
- Lomakkeet on suojattu **CSRF-tokeneilla** kurssimateriaalin mallin mukaisesti.

-Asennus ja käynnistys

1. Kloonaa repository

git clone https://github.com/7URF1N/recipe-app
cd recipe-app

2. Luo ja aktivoi virtuaaliympäristö

Windows (PowerShell):
python -m venv venv
venv\Scripts\activate

macOS / Linux:
python3 -m venv venv
source venv/bin/activate

3. Asenna riippuvuudet

pip install flask

4. Luo tietokanta

Windows (PowerShell):
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql

macOS / Linux:
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql

Jos koneessasi ei ole `sqlite3`-komentorivityökalua, voit luoda tietokannan
Pythonilla:

python -c "import sqlite3; con=sqlite3.connect('database.db'); \
con.executescript(open('schema.sql').read()); \
con.executescript(open('init.sql').read()); con.commit(); con.close()"

Jos sinulla on jo vanha `database.db`, poista se ennen kuin luot uuden:

- Windows: `del database.db`
- macOS / Linux: `rm database.db`

5. Käynnistä sovellus

flask --app app run

tai vaihtoehtoisesti:

python app.py


Sovellus käynnistyy osoitteeseen <http://127.0.0.1:5000>.

-Sovelluksen testaaminen

1. Avaa selain osoitteessa <http://127.0.0.1:5000>. Etusivu näkyy myös ilman
   kirjautumista.
2. Klikkaa **Rekisteröidy** ja luo uusi tunnus (esim. `testi` / `salasana`).
3. Kirjaudu sisään.
4. Klikkaa **Uusi resepti**. Täytä nimi, ainekset ja ohjeet. Valitse
   luokitteluja eri kategorioista (esim. Tyyppi: *Pääruoka*, Keittiö:
   *Italialainen*, Ruokavalio: *Kasvis*). Paina **Tallenna**.
5. Siirry reseptin sivulle etusivun kautta. Kokeile **Muokkaa**- ja
   **Poista**-nappeja.
6. Luo toinen tunnus ja kirjaudu sillä sisään. Avaa ensimmäisen käyttäjän
   resepti ja jätä siihen kommentti sekä tähtiarvio. Kommentin pitäisi näkyä
   reseptin sivulla, ja reseptin keskiarvon pitäisi päivittyä.
7. Klikkaa navigointipalkissa käyttäjänimeäsi. Käyttäjäsivu näyttää tilastot
   ja omat reseptisi.
8. Kokeile hakutoimintoa navigointipalkin **Haku**-linkin kautta.

Vieras-avaimet on päällä (`PRAGMA foreign_keys = ON`), joten reseptin
poistaminen poistaa automaattisesti myös sen kommentit ja luokittelut.

Pylint score: Your code has been rated at 8.15/10