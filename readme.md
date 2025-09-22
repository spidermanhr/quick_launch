Quick Launcher
---
Quick Launcher je aplikacija napisana u **Pythonu** koja na intuitivan način prikazuje sve instalirane programe na vašem računalu, omogućujući vam da ih brzo pokrenete s prilagodljivog sučelja.

### Značajke

* **Optimiziran prikaz**: Automatski prilagođava broj stupaca kako bi prozor bio što širi i kraći, čime efikasno iskorištava prostor na ekranu.
* **Dinamična veličina**: Prozor se automatski prilagođava broju aplikacija, ali nikada ne prelazi 50% širine i visine ekrana.
* **Automatsko pomicanje**: Ako ima previše aplikacija, klizač se automatski pojavljuje.
* **Fiksna pozicija**: Uvijek se pokreće u donjem lijevom kutu zaslona, bez preklapanja s taskbarom.
* **Prilagodljive postavke**: Omogućuje vam da odaberete koje aplikacije želite vidjeti, a koje želite sakriti. Postavke se spremaju za buduće korištenje.

---

### Upute za korištenje

Da biste pokrenuli aplikaciju, slijedite ove korake.

#### 1. Instalacija potrebnih alata

Aplikacija je napisana u Pythonu i za ispravan rad zahtijeva instalaciju biblioteke **pywin32** i **PyInstaller** (ako želite aplikaciju pakirati u **.exe** datoteku).

Otvorite terminal (npr. Command Prompt) i instalirajte ih pomoću sljedeće naredbe:

`pip install pywin32 pyinstaller`

*Napomena: Pillow biblioteka nije potrebna za ovu aplikaciju.*

#### 2. Pokretanje aplikacije

* **Pokretanje kao Python skripta**: Pokrenite datoteku s nastavkom `.py` (npr. **quick_launcher.py**) iz terminala naredbom `python ime_datoteke.py`.
* **Izrada samostalne aplikacije (.exe)**: Ako želite stvoriti samostalni **.exe** program, otvorite terminal u istom direktoriju kao i `.py` datoteka te pokrenite ovu naredbu:

    `pyinstaller --onefile --windowed ime_datoteke.py`

Gotova **.exe** datoteka nalazit će se u novostvorenom direktoriju **dist**.
