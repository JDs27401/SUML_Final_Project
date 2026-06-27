# SUML_Final_Project – System Predykcji Wyników Meczów Piłkarskich

## Autorzy
- **s27401** Dominik Juchniewicz
- **s27016** Bartosz Kowalski
- **s25402** Miłosz Pawłowski

---

## 1. Wstęp i Cel Projektu

Projekt realizuje zadanie prognozowania wyników międzynarodowych meczów piłki nożnej z wykorzystaniem metod uczenia maszynowego. Istotą systemu jest odejście od prostej klasyfikacji trójstanowej (wygrana / remis / przegrana) na rzecz podejścia regresyjnego. Model uczy się przewidywać ciągłą wartość różnicy bramek pomiędzy gospodarzem a gościem. 

Takie rozwiązanie pozwala na wskazanie faworyta spotkania.
---

## 2. Architektura Systemu

System składa się z czterech odseparowanych warstw logicznych, uruchamianych w dwóch niezależnych procesach komunikujących się przez protokół HTTP (REST API):

1. **Warstwa Prezentacji (`Frontend - Streamlit`)**: Odpowiada za interakcję z użytkownikiem, walidację danych wejściowych w formularzach oraz renderowanie statystyk, tabel i predykcji pobranych z API.
2. **Warstwa Usługowa (`Backend API - FastAPI`)**: Oparta na Uvicorn. Klasy `Pydantic` gwarantują ścisłe sprawdzanie typów przesyłanych struktur JSON.
3. **Warstwa Wnioskowania (`ML / Predictor`)**: Silnik predykcyjny odpowiadający za transformację danych wejściowych, ładowanie artefaktu `.joblib` oraz przeliczanie przewag regresyjnych na konkretne bramki.
4. **Warstwa Danych (`Data / Pandas`)**: Realizuje zadania inżynierii cech, przeszukując historyczne szeregi czasowe w celu wyliczenia formy obu zespołów.

---

## 3. Struktura Katalogów i Modułów

    SUML_Final_Project/
    ├── App/
    │   ├── __init__.py          # Inicjalizacja pakietu aplikacji
    │   ├── api.py               # Główny serwer FastAPI, definicje endpointów
    │   └── app.py               # Klient Streamlit
    ├── Data/
    │   ├── __init__.py          # Inicjalizacja pakietu aplikacji
    │   ├── football_data.py     # Logika inżynierii cech i agregacji danych
    │   ├── former_names.csv     # Słownik historycznych nazw państw i reprezentacji
    │   ├── goalscorers.csv      # Baza danych strzelców bramek
    │   ├── results.csv          # Główna baza historycznych wyników meczów od XIX wieku
    │   └── shootouts.csv        # Statystyki rzutów karnych
    ├── Model/
    │   ├── artifacts/
    │   │   └── football_match_linear_regression.joblib  # Wytrenowany model 
    │   ├── __init__.py          # Inicjalizacja pakietu aplikacji
    │   ├── model_training.py    # Potok treningowy
    │   └── predictor.py         # Logika klasyfikacji wyników i estymacji bramek
    ├── .gitignore               # Wykluczenia plików z repozytorium Git
    ├── .python-version          # Definicja wymogu wersji interpretera
    ├── README.md                # Niniejsza dokumentacja techniczna
    ├── requirements.txt         # Wykaz zależności bibliotecznych
    ├── run_api.bat              # Skrypt uruchamiający wyłącznie backend API
    ├── run_app.bat              # Główny skrypt automatyzujący środowisko i start całego systemu
    └── run_streamlit.bat        # Skrypt uruchamiający wyłącznie frontend Streamlit

### Opis najważniejszych modułów:
* **`Data/football_data.py`**: Zawiera algorytmy operujące na bazie `results.csv`. Funkcja `calculate_recent_team_statistics` przeszukuje historię wstecz od wybranej daty meczu, aby wyekstrahować dokładnie zadany limit (`FORM_MATCH_LIMIT = 20`) ostatnich spotkań dla obu zespołów i wyliczyć ich aktualną formę.
* **`Model/model_training.py`**: Tworzy `ColumnTransformer`, uczy algorytm regresji liniowej, wylicza błędy testowe i zapisuje gotowy potok do pliku `.joblib`.
* **`Model/predictor.py`**: Odpowiada za inference. Łączy formę historyczną z parametrami meczu, przepuszcza przez model i implementuje stałą `DRAW_THRESHOLD = 0.35`.

---

## 4. Potok Machine Learning i Przetwarzanie Danych

### Inżynieria Cech
Model nie uczy się na statycznych nazwach drużyn, co zapobiega przeuczeniu. Dla każdego meczu w zbiorze generowane jest wejściowe okno formy z 20 ostatnich spotkań:

* **Cechy numeryczne**: 
  * `home_winrate` / `away_winrate` – procent wygranych spotkań w analizowanym oknie.
  * `home_gf` / `away_gf` – średnia strzelonych goli na mecz.
  * `home_ga` / `away_ga` – średnia straconych goli na mecz.
* **Cechy kategoryczne**: 
  * `tournament` – ranga rozgrywek.
  * `country` – kraj rozgrywania meczu.
  * `neutral` – zmienna binarna, czy boisko jest neutralne.

### Preprocessing Pipeline
1. **Standaryzacja (`StandardScaler`)**: Cechy numeryczne są sprowadzane do średniej $0$ i wariancji $1$, co stabilizuje obliczenia regresji liniowej.
2. **Kodowanie 1 z n (`OneHotEncoder`)**: Zmienne tekstowe zamieniane są na macierze binarne. Parametr `handle_unknown="ignore"` zapobiega błędom aplikacji przy próbie predykcji turnieju niewystępującego w danych treningowych.

### Model Regresji i Próg Remisu
* **Algorytm**: `LinearRegression`.
* **Cel (Target)**: `home_score - away_score`.
* **Klasyfikacja**: Wynik ciągły $\hat{y}$ jest mapowany na decyzję za pomocą szerokości pasma remisu (`DRAW_THRESHOLD = 0.35`):
  * Wygrana Gospodarzy: $\hat{y} > 0.35$
  * Wygrana Gości: $\hat{y} < -0.35$
  * Remis: $-0.35 \le \hat{y} \le 0.35$

---

## 5. Instrukcja Instalacji i Uruchomienia

### Wymagania środowiskowe
* **System operacyjny**: Microsoft Windows.
* **Interpreter**: Python w wersji **3.14**.

### Automatyczny Start (Zalecany)
W katalogu głównym projektu kliknij dwukrotnie lub wywołaj w konsoli:

    .\run_app.bat

**Skrypt automatycznie wykona całą inicjalizację:**
1. Sprawdzi obecność folderu `.venv` (jeśli go nie ma – utworzy środowisko wirtualne).
2. Zainstaluje brakujące pakiety z `requirements.txt`.
3. Uruchomi serwer FastAPI w tle na porcie `8000`.
4. Uruchomi interfejs Streamlit i otworzy projekt w domyślnej przeglądarce pod adresem `http://localhost:8501`.

*(Uwaga: Przy pierwszym uruchomieniu biblioteka Streamlit może poprosić w konsoli o adres e-mail – **wciśnij klawisz Enter**, aby pominąć).*

### Ręczne uruchamianie warstw (Z poziomu dwóch terminali)

Jeśli chcesz podglądać logi backendu i frontendu niezależnie:

**Terminal 1 (Backend API):**
    .\run_api.bat
    # LUB bez skryptu: uvicorn App.api:app --reload --port 8000

**Terminal 2 (Frontend UI):**
    .\run_streamlit.bat
    # LUB bez skryptu: streamlit run App/app.py

---

## 6. Sposób użycia aplikacji

1. W panelu bocznym zweryfikuj aktualne metryki modelu ML (`MAE`, `R2 Score`) oraz datę jego wytrenowania.
2. Wybierz **Drużynę 1** oraz **Drużynę 2**.
3. Określ status boiska.
4. Wybierz rozgrywki, kraj oraz planowaną datę rozegrania meczu.
5. Kliknij **"Predict Match"**.
6. Zapoznaj się z werdyktem modelu, szacowanym dokładnym wynikiem bramkowym oraz tabelą porównawczą formy z ostatnich 20 spotkań obu reprezentacji.

---

## 7. Specyfikacja Interfejsu API

Serwer udostępnia cztery główne punkty końcowe komunikujące się przez format JSON:

### `GET /health`
Szybki test sprawności usługi (zwraca `{"status": "healthy"}`).

### `GET /metadata`
Zwraca listy unikalnych drużyn, turniejów i państw na potrzeby frontendu oraz parametry jakościowe estymatora.

### `POST /predict`
Przyjmuje wektor cech planowanego meczu i zwraca kompletny werdykt regresyjny. Przykład wejścia:
```json
{
  "home_team": "Poland",
  "away_team": "Germany",
  "tournament": "FIFA World Cup",
  "match_country": "United States",
  "is_neutral_ground": true,
  "match_date": "2026-06-28"
}
```

### `POST /retrain`
Wymusza natychmiastowe przeliczenie cech z pliku `results.csv` i wygenerowanie nowego pliku artefaktu `.joblib` w locie.
