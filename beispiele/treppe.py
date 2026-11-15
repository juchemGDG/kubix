from kubix import *

welt = Welt(10, 10)
figur = Figur(welt)

# Eine Treppe bauen und hinaufsteigen: Stufe 1 ist 1 Block hoch, Stufe 2 ist 2 Blöcke hoch, ...
for stufe in range(1, 5):
    for _ in range(stufe):
        figur.baue("stein")
    figur.gehe(1)
    figur.sage(f"Stufe {stufe} geschafft!", 1)
