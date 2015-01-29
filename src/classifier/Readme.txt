# Slikto teikumu filtrēšana

Šis rīks ar mašīnmācīšanos iemācās no fīčām, kuri teikumi ir slikti. Pēc tam rīku var uzlaist īstiem teikumiem un tiks atlasīti tikai labie.

## Struktūra

Mape `app` satur Java komandrindas programmas kodu, kura izmanto no Weka mašīnmācīšanās bibliotēkas J48 mašīnmācīšanās algoritmu. `app.jar` ir jau nokompilēta, palaižama (ar java) programma.

## Instrukcijas

Vispirms vajag uztrennēt modeli, kas mācēs pateikt no fīčām, vai teikums ir labs vai slikts. Fīčām jābūt sekojošā formātā (t.i. atdalītām ar `\t`):

    -141.1955319178	-118.2339517043	0.5454545455	0.6666666667	good
    -15.0269511771	-17.0282278854	0.7500000000	0.7500000000	good
    -154.4069509328	-146.1149283592	0.5555555556	0.6060606061	bad
    -154.4069509328	-146.1149283592	0.5555555556	0.6060606061	bad

Uztrennēt var ar sekojošu komandu:

  java -jar app.jar
    -train
    -m 100k.model
    -f test/data/gen/100k/train.features.txt
    -e test/data/gen/100k/test.features.txt

`-train` norāda, ka šoreiz būs jātrennē modelis, `-m` norāda failu, kurā saglabāt uztrennēto modeli, `-f` norāda uz failu, kurā ir fīčas, no kurām mācīties (tur jābūt gan good, gan bad piemēriem), `-e` nav obligāts, bet ja ir norādīts, tad uzrīdīs 10-fold cross validation uz fīčām no šī faila un izdrukās rezultātus.

Pēc tam, kad nepieciešams iztīrīt korpusu, to var izdarīt šādi:

    java -jar app.jar 
      -m 100k.model
      -f test/data/gen/100k/check.features.txt
      -s test/data/gen/100k/check.corpus.src.txt
      -t test/data/gen/100k/check.corpus.trg.txt
      -os test/data/gen/100k/check.corpus.src.f.txt
      -ot test/data/gen/100k/check.corpus.trg.f.txt

`-m` norāda uz saglabātā modeļa faila nosaukumu, `-f` ir uztaisītās fīčas korpusam, `-s` ir teikumi (katrs teikums savā rindiņā) vienā valodā un `-t` ir teikumi otrā valodā, `-os` norāda uz failu, kurā tiks ierakstīti tikai labie teikumi vienā valodā un `-`ot` norāda uz failu, kurā tiks ierakstīti tikai labie teikumi otrā valodā.

## Testēšana

Mape `test`.

Mapē `test/data` ir no kaut kurienes nākuši dati. Tie, kas satur `good` nosaukumā, acīmredzot ir labi dati, `bad` ir acīmredzot slikti dati t.i. teikumi nesakrīt tajos. `gen.py` skripts mapē `test/data/gen` saģenerēs dažāda lieluma failus ar apvienotiem labiem un sliktiem datiem, lai tos varētu izmantot testēšanā. Šo skriptu var palaist arī ar `data.bat`.

`train.bat` un `test.bat`, kuri satur piemērus, kā izsaukt programmu, izmanto šos uzģenerētos failus.
