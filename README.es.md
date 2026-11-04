# Cashflow Bridge Check

CLI local para conciliar flujos de efectivo con importes decimales exactos. Requiere **Python 3.11+** y solo su biblioteca estándar. Sin claves, modelos ni conexiones de red durante el cálculo.

[English](README.md) · [Cashflow Fieldnotes](https://filings.findfindata.com/es/)

## Ejecución

```sh
git clone https://github.com/faigvain-ang/cashflow-bridge-check.git
cd cashflow-bridge-check
python cashflow_bridge.py examples/reconciled.json --json
python -m unittest discover -s tests -v
python site/build.py
```

Utilice `python3` si ese es el nombre del intérprete en su sistema. No hay dependencias externas de ejecución ni pruebas, y no hace falta un entorno virtual.

## Entrada y resultado

`examples/reconciled.json` es un ejemplo sintético: USD, millones, ejercicio FY2025 y el mismo perímetro de efectivo y equivalentes al principio y al final. Debe incluir `period`, `currency`, `unit`, `cash_basis` y los seis importes como **cadenas JSON**, no números.

- `opening`: `"100"`; `operating`: `"35"`.
- `investing`: `"-20"`; `financing`: `"-10"`.
- `fx`: `"-2"`; `closing`: `"103"`.

La fórmula es `opening + operating + investing + financing + fx + ajustes explícitos`. Las **salidas netas llevan signo negativo**; no invierta de nuevo un importe ya negativo. `fx` es obligatorio: escriba `"0"` solo tras comprobar que no existe efecto cambiario. Resultado: cierre calculado `103`, cierre declarado `103`, diferencia `0`, `matches: true`. La diferencia es siempre **declarado menos calculado**.

`--tolerance 0.01` indica tolerancia absoluta en la unidad de entrada: en millones equivale a 10.000 unidades monetarias. `--tolerance 0` exige igualdad exacta. Códigos de salida: **0** coincide, **1** no coincide, **2** entrada o uso inválido. Los ajustes opcionales deben tener etiqueta y cantidad, por ejemplo `{"label":"Cambio de perímetro","amount":"5"}`; no use una partida de cuadre sin respaldo.

## Límites

Comprueba aritmética, no veracidad financiera. No lee PDF, no descubre omisiones, no convierte monedas ni unidades y no comprueba automáticamente el perímetro del efectivo. Revise período, signos, unidad y definición en la fuente. No ofrece recomendaciones de inversión. Rechaza valores no finitos e importes JSON numéricos; ajusta la precisión Decimal para conservar los decimales suministrados.

## Documentación y recursos

Ejecute `python site/build.py` para generar las guías bilingües en `docs/` a partir de `site/config.json` y `site/content.json`.

Para investigar las cuestiones que plantee la conciliación, consulte [Eqvero](https://eqvero.com/) y su [espacio de investigación empresarial](https://eqvero.com/companies), con referencias a información pública.

Licencia MIT. Sin dependencias externas. Todos los ejemplos son sintéticos.
