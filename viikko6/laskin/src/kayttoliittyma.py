from enum import Enum
from tkinter import ttk, constants, StringVar


class Komento(Enum):
    SUMMA = 1
    EROTUS = 2
    NOLLAUS = 3
    KUMOA = 4


class Kayttoliittyma:
    def __init__(self, sovelluslogiikka, root):
        self._sovelluslogiikka = sovelluslogiikka
        self._root = root

        self._komennot = {
            Komento.SUMMA: Summa(sovelluslogiikka, self._lue_syote),
            Komento.EROTUS: Erotus(sovelluslogiikka, self._lue_syote),
            Komento.NOLLAUS: Nollaus(sovelluslogiikka),
        }
        self._viimeisin_komento = None

    def kaynnista(self):
        self._arvo_var = StringVar()
        self._arvo_var.set(self._sovelluslogiikka.arvo())
        self._syote_kentta = ttk.Entry(master=self._root)

        tulos_teksti = ttk.Label(textvariable=self._arvo_var)

        summa_painike = ttk.Button(
            master=self._root,
            text="Summa",
            command=lambda: self._suorita_komento(Komento.SUMMA)
        )

        erotus_painike = ttk.Button(
            master=self._root,
            text="Erotus",
            command=lambda: self._suorita_komento(Komento.EROTUS)
        )

        self._nollaus_painike = ttk.Button(
            master=self._root,
            text="Nollaus",
            state=constants.DISABLED,
            command=lambda: self._suorita_komento(Komento.NOLLAUS)
        )

        self._kumoa_painike = ttk.Button(
            master=self._root,
            text="Kumoa",
            state=constants.DISABLED,
            command=lambda: self._suorita_komento(Komento.KUMOA)
        )

        tulos_teksti.grid(columnspan=4)
        self._syote_kentta.grid(columnspan=4, sticky=(constants.E, constants.W))
        summa_painike.grid(row=2, column=0)
        erotus_painike.grid(row=2, column=1)
        self._nollaus_painike.grid(row=2, column=2)
        self._kumoa_painike.grid(row=2, column=3)

    def _lue_syote(self):
        return self._syote_kentta.get()

    def _suorita_komento(self, komento):
        if komento == Komento.KUMOA:
            if self._viimeisin_komento:
                try:
                    self._viimeisin_komento.kumoa()
                except Exception:
                    pass
                self._viimeisin_komento = None
            self._kumoa_painike["state"] = constants.DISABLED
        else:
            komento_olio = self._komennot[komento]
            komento_olio.suorita()
            self._viimeisin_komento = komento_olio
            self._kumoa_painike["state"] = constants.NORMAL

        if self._sovelluslogiikka.arvo() == 0:
            self._nollaus_painike["state"] = constants.DISABLED
        else:
            self._nollaus_painike["state"] = constants.NORMAL

        self._syote_kentta.delete(0, constants.END)
        self._arvo_var.set(self._sovelluslogiikka.arvo())

class Summa:
    def __init__(self,sovelluslogiikka,lue_syote):
        self._sovellus = sovelluslogiikka
        self._lue_syote = lue_syote
        self._edellinen = 0

    def suorita(self):
        try:
            operand = int(self._lue_syote())
        except Exception:
            operand = 0
        self._edellinen = self._sovellus.arvo()
        self._sovellus.plus(operand)

    def kumoa(self):
        self._sovellus.aseta_arvo(self._edellinen)

class Erotus:
    def __init__(self,sovelluslogiikka,lue_syote):
        self._sovellus = sovelluslogiikka
        self._lue_syote = lue_syote
        self._edellinen = 0
        
    def suorita(self):
        try:
            operand = int(self._lue_syote())
        except Exception:
            operand = 0
        self._edellinen = self._sovellus.arvo()
        self._sovellus.miinus(operand)

    def kumoa(self):
        self._sovellus.aseta_arvo(self._edellinen)

class Nollaus:
    def __init__(self,sovelluslogiikka):
        self._sovellus = sovelluslogiikka
        self._edellinen = 0
        
    def suorita(self):
        self._edellinen = self._sovellus.arvo()
        self._sovellus.nollaa()

    def kumoa(self):
        self._sovellus.aseta_arvo(self._edellinen)