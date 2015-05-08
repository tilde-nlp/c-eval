Vārdu sastatītājs
=================

Šis rīks apvieno GIZA++ un fastalign. Palaižot šo rīku ar ievaddatiem un norādot vienu vai otru sastatītāju, izvaddati abiem būs vienādi. Taču, ja nepieciešams, var saglabāt oriģinālos izvaddatus arīdzan. Šis rīks darbojas gan uz Windows, gan uz Linux: rīks izsauc atbilstošās fastalign un giza programmas.

Lietošana no komandrindas
-------------------------

Lietošanas piemērs. 

Ir paralēls angļu-latviešu korpuss, kurš atrodas divos failos: `en.txt` un `lv.txt`.
Katrā faila rindiņā ir teikums, katrs tokens katrā teikumā ir atdalīts ar atstarpi.

Ar `-a` vai `--aligner` norāda, kuru sastatījumu lietot.

Atbalstītie sastatītāji:
* `giza` ir GIZA++
* `fastalign` ir fast align

Avota korpusa failu noarāda ar `-s` vai `--source-file`, mērķa korpusu norāda ar `-t` vai `--target-file`.

Avota-mērķa sastatījuma izvadfailu norāda ar `-st` vai `--source-target-file`, 
bet mērķa-avota sastatījuma izvadfailu ar `-ts` vai `--target-source-file`.
Norādīt var vienu vai abus.

Lai izveidotu angļu-latviešu vārdu sastatījumu ar GIZA++, var izsaukt:

    python aligner.py \
      -a giza         \
      -s en.txt       \
      -t lv.txt       \
      -st en-lv.txt

Lai izveidotu latviešu-angļu vārdu sastatījumu ar GIZA++, var izsaukt:

    python aligner.py \
      -a giza         \
      -s en.txt       \
      -t lv.txt       \
      -ts lv-en.txt

Lai izveidotu gan angļu-latviešu, gan latviešu-angļu vārdu sastatījumu ar GIZA++, var izsaukt abas iepriekš minētās komandas, vai arī tikai ar vienu komandu:

    python aligner.py \
      -a giza         \
      -s en.txt       \
      -t lv.txt       \
      -st en-lv.txt   \
      -ts lv-en.txt

Lai izveidotu angļu-latviešu vārdu sastatījumu ar fastalign, var izsaukt:

    python aligner.py \
      -a fastalign    \
      -s en.txt       \
      -t lv.txt       \
      -st en-lv.txt

Ja nepieciešams padot parametrus GIZA++ vai fastalign, to var izdarīt ar `-x` vai `--aligner-args`.

Noklusētie parametri:
* GIZA++ `-m1 5 -m2 0 -m3 3 -m4 3 -model1dumpfrequency 1 -model4smoothfactor 0.4 -nodumps 1 -nsmooth 4 -onlyaldumps 1 -p0 0.999`
* fastalign `-d -o -v`

Piemērs:

    python aligner.py \
      -a fastalign    \
      -x "-N -I 10"   \
      -s en.txt       \
      -t lv.txt       \
      -st en-lv.txt

Pēc noklusējuma visa izvade un kļūdu izvade tiek drukāta uz `stdout`.
To visu var saglabāt failā, pieliekot komandai beigās `> file.log` 
vai arī ar parametru `-l` vai `--log-file`: `--log-file file.log`.

Gan GIZA++, gan fastalign izmantošanas laikā tiek izveidoti daudzi starpfaili mapē, kurā atrodas avota un mērķa ievaddati.
Šie faili beigās tiek izdzēsti. Ja tie nepieciešami, var izmantot `-k` vai `--keep-extra` parametru.

Iepriekš minēto komandu lietošanas piemērs:

    python aligner.py \
      -a fastalign    \
      -s en.txt       \
      -t lv.txt       \
      -st en-lv.txt   \
      -l en-lv.log    \
      --keep-extra

Dažreiz nepieciešams paturēt dažus, bet ne visus starp failus.
To var izdarīt, ar speciāliem parametriem.
Šiem parametriem var norādīt vērtību, kas ir faila nosaukums.
Ja nav norādīta vērtība, tad tiek izmantots sastatījuma izvadfaila nosaukums ar attiecīgu paplašinājumu.

Parametri:
* `--giza-keep-output` patur GIZA++ sastatījumus, kas ir trīs rindiņas katram teikumam: `.giza`
* `--giza-keep-cfg` patur GIZA++ ģenerēto konfigurācijas failu: `.gizacfg`
* `--fastalign-keep-input` patur fast align ievaddatus: `.fastalign.input`
* `--fastalign-keep-table` patur fast align varbūtību tabulu: `.fastalign.table`

GIZA++ piemērs.
Oriģinālie izvaddati tiks saglabāti failā `en-lv.txt.giza`
un parametru fails failā `en-lv.gizalog`.

    python aligner.py                 \
      -a giza                         \
      -s en.txt                       \
      -t lv.txt                       \
      -st en-lv.txt                   \
      --giza-keep-output              \
      --giza-keep-cfg "en-lv.gizalog"

Lietošana no Python
-------------------------

Sastatītāju var lietot arī no Python koda.

Piemērs:

    import aligner
    
    aligner.giza('en.txt', 'lv.txt', 'en-lv.txt', open('en-lv.log', 'w'), 
                 keep_output='en-lv.giza.txt')

Modulis satur arī papildus citas funkcijas:

* `fastalign_create_inputfile`
* `giza_convert_alignments`
* `giza_convert_alignments_line`

Lietošanai nepieciešamās bibliotēkas
------------------------------------

Uz Windows nepieciešams Visual C++ Redistributable Packages for Visual Studio 2013:
http://www.microsoft.com/en-us/download/details.aspx?id=40784

Uz Linux nav nepieciešams nekas, jo programmas ir kompilētas statiski.

GIZA++ un fastalign programmu kompilēšana
-----------------------------------------

### GIZA++

**Windows**

    git clone https://github.com/tilde-nlp/giza-pp
    git checkout vs2013
    build.ps1

**Linux**

    git clone https://github.com/tilde-nlp/giza-pp
    git checkout static
    make dist

### fastalign

**Windows**

    git clone https://github.com/tilde-nlp/fast_align
    git checkout windows
    C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe fast_align.vcxproj /p:Configuration=Release

**Linux**

    git clone https://github.com/tilde-nlp/fast_align
    git checkout static
    make static

TODO
----

* error handligns
* automatizēti testi
* GIZA++: faili, kas nebeidzas ar .txt vai .tok
* CMake priekš fast align kompilēšanas
