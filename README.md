# ReseptiApp
Pythonilla ja Flaskilla rakennettu full-stack -verkkosovellus, joka mahdollistaa käyttäjille reseptien luomisen, tarkastelun ja hallinnan.

## Asennus ja käynnistys
1. git clone https://github.com/7URF1N/recipe-app

2. cd recipe_app 

3. python -m venv venv

4. Windows:
venv\Scripts\activate
Mac:
venv/bin/activate

5. pip install flask
set FLASK_APP=app.py
flask init-db

huom jos tulee ongelma on vanha recipes.db jossa on eri rakenne. Poista se ja luo uusi eli:
del recipes.db
set FLASK_APP=app.py
flask init-db

6. python app.py

7. Avaa: http://127.0.0.1:5000

## Toiminnot

- Rekisteröinti ja kirjautuminen
- Reseptien lisäys, muokkaus, poisto
- Haku nimellä tai ainesosalla + kategoriafiltteri
- Arviot ja kommentit (toissijainen tietokohde)
- Profiilisivu