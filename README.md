# SUML_Final_Project

## Aplikacja Streamlit przewidujaca wynik meczu pilkarskiego na podstawie regresji liniowej.
* Działanie aplikacji opiera się na wybraniu drużyn A i B
* Następnie należy wybrać która drużyna jest drużyną gospodarzy, a w przypadku turniejów albo braku gospodarza można wybrać opcję bez
* Forma meczu, np.: Friendly albo FIFA World Cup, określa typ rozgrywek 

## Wynik jest przedstawiany jako:
1. Najpierw drużyna która według modelu wygra
2. Przybliżony wynik meczu oraz delta bramek które strzelą drużyny, wyliczana jako różnia goli drużyny A - B
3. Szcowane gole określa ile bramek (w formie ułamkowej) strzeli drużyna według modelu. Z tych wartości jest brany przewidywany wynik
4. Tabela przedstawia statystyki drużyn oraz ilość meczy przekazanych do modelu

### Cechy modelu pozwalają podejrzeć konkretne wartości jakie zostały przekazane

## Uruchomienie calej aplikacji

```run_app.bat - uruchamia backend jak i front end```

## Uruchamianie frontend'u

```run_streamlit.bat```

## Uruchamianie tylko backend'u

```run_api.bat```

## Endpointy API:

- `GET /health`
- `GET /metadata`
- `POST /predict`
- `POST /retrain`

### Model trenuje sie automatycznie przy pierwszym uruchomieniu i zapisuje artefakt w ```Model/artifacts```.
