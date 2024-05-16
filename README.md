# SOLUTION_OF_OPTIMIZATION_TASKS_FOR_ELECTRIC_CARS
Riešim problém vehicle routing pre elektrické vozidlá, ktorý je v dnešnej dobe zaujímavý a trendy. Ide o NP-ťažký problém, kde máme dané dáta o depách, zákazníkoch a nabíjacích staniciach so súradnicami, kapacitu áut a elektrickú kapacitu vozidiel. Cieľom je nájsť najlepšie riešenie pre doručenie nákladu všetkým zákazníkom.

Používam benchmarky zo súťaže z roku 2020, čo mi umožňuje porovnať môj algoritmus s výsledkami súťaže. Začínam s menšími dátami a postupne prechádzam na väčšie dátové sady.

Zatiaľ som naštudoval problematiku, určil ciele, vytvoril prvú implementáciu na načítanie benchmarkov a vrátenie najlepšej cesty pomocou náhodného generovania ciest, a pripravil kostru v LaTeXe s prvými stránkami teórie ACO.

Venujem sa optimalizácii Ant Colony Optimization (ACO), kde využívam feromónovú maticu na výber ciest. Riešim správny výber ďalšieho bodu v ceste, berúc do úvahy obmedzenia ako kapacita vozidla a nabíjanie. Dôležité je tiež nájsť vhodné nastavenie parametrov ako "počet mravcov", alfa, beta, atď.

# Kalendár Cieľov
1. Začiatok práce
   - Pochopiť dôležité apsekty diplomovej práce. Rozvrhnút si úlohy. Prvé kroky v implementácií. Získanie a študovanie literatúry.
   - 16.5.2024
2. Úplné definovanie benchmarkov
   - Popis a pochopenie vstupných dát
   - 31.7.2024
3. Návrh a implementácia môjho použitia ACO
   - Zohľadnenie všetkých obmedzení
   - 30.9.2024
4. Zobrazovanie výstupov do grafov a tabuliek
   - Vizualizácia problému
   - Možnosť porovnania
   - 30.9.2024
5. Paralelizovať riešenie
   - 30.10.2024
6. Skvalitnenie kódu
   - 31.12.2024
7. Skúmanie mojich výsledkov
   - Porovnanie s už vytvorenými výsledkami
   - 20.2.2025
8. Sumarizácia a dokončenie textu diplomovej práce
   - 31.3.2025
