'cleaner.py' skripts attīra paralēlos korpusus (izveitdo failu ar "labiem" teikumiem, balstoties uz iepriekšizveidota mašīnmācīšanās modeļa). "Labs" teikums ir tāds, kura rādītāji pārvar "laba" teikuma slieksni balstoties uz uztrennēto modeli. Paralēls korpus ir divi teksta faili, kur katrs teikums atrodas jaunā līnijā, tulkotie tokeni atdalīti ar tukšumu (tokenizēts teksts), un teikumi ir tulkoti no vienas valodas uz otru, atbilstoši pa līnijām. Iespējams lietot divas sastatīšanas programmas: giza (laba, bet lēna, vidēji 50'000 līnijas aizņems kādu 1.5 h) un fastalign (pielīdzināmi labs, bet ātrāks, vidēji 50'000 līniju aizņems 0.5 h). Ja nav bijusi kļūda un sastatīšanas process notiek, bet ļoti lēnām, pastāv iespēja, ka datoram ir pārpildīta atmiņa. Tad ieteicams laist eksperimentu ar mazāku korpusu. 

Lai varētu izvilkt "labos" teikumus:
1) Moduļa trennēšana, kurā ir gan labi dati, gan slikti dati. (slikti dati ģenerējas automātiski)
Dati šeit un turpmāk apzīmē paralēlu korpusu ar teikumiem divās valodās.
Labi dati ir tādi, kur katram teikumam ir pareizs tulkojums.
Slikti dati ir tādi, kur katram teikumam ir nepareizs tulkojums.

Sliktos datus var uzģenerēt ar python skriptu `shuffle.py`.
Šis skripts teikumus no faila vienā valodā sajauc jauktā secībā.

Trenēšana:
  GOOD
  * paņem labu paralēlu korpusu
  * sastata labo paralēlo korpusu
  * uzģenerē īpašības labajiem sastatījumiem
  BAD
  * paņem labu paralēlu korpusu
  * sakropļo teikumu sastatījumus labajam paralēlajam korpusam
  * sastata sakropļotos sastatījumus
  * uzģenerē īpašības sakropļotajiem sastatījumiem
  GOOD+BAD
  * savieno GOOD un BAD īpašības
  * uztrennē modeli

Skripta piemērs:
    python cleaner.py -train TRAIN 
		      -s en.100k.txt 
		      -t lv.100k.txt 
		      -a giza 
		      -c extratrees 
		      -m en-lv.10k.giza.extratrees.model

Kur -train norāda, ka jātrennē modelis, -s ir source corpus, -t target courpus, -a aligner (sastatīšanas programma), kur var norādīt vai nu giza, vai fastalign, -c ir classifier (mašīnmācīšanās algoritms), izvēles iespējas: extratrees, j48
-m ir izveidotā modeļa nosaukums

2) Paralēlā korpusa tīrīšana:
  * paņem paralēlu korpusu
  * sastata paralēlu korpusu
  * uzģenerē īpašības paralēlajam korpusam
  * izfiltrē paralēlo korpusu ar jau uztrenētu modeli

Skripta piemērs:
	python cleaner.py -a giza 
			  -s en.10k.txt 
			  -t lv.10k.txt 
			  -m en-lv.100k.giza.extratrees.model

Kur -m ir iepriekš uztrennētais modelis

Argumenti jānorāda unikāli no failiem, kas jau atrodas direktorijā. Procesu vajag palaist no direktorijas, kur ir korpuss, un uz ".../bin/cleaner.py"  norāda pilno ceļu.

Rezultātā izliftrētie faili būs atrodami mapē pie korpusa ar atslēgas vārdu 'filtered' (en.10K.txt.filtered.txt un lv.10K.txt.filtered.txt).