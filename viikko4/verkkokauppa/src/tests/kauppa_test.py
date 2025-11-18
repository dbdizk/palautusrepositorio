import unittest
from unittest.mock import Mock, ANY, call
from kauppa import Kauppa
from viitegeneraattori import Viitegeneraattori
from varasto import Varasto
from tuote import Tuote
from kirjanpito import Kirjanpito

class TestKauppa(unittest.TestCase):
    def test_maksettaessa_ostos_pankin_metodia_tilisiirto_kutsutaan(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        # palautetaan aina arvo 42
        viitegeneraattori_mock.uusi.return_value = 42

        varasto_mock = Mock()

        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)

        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.tilimaksu("pekka", "12345")

        # varmistetaan, että metodia tilisiirto on kutsuttu
        pankki_mock.tilisiirto.assert_called()
        # toistaiseksi ei välitetä kutsuun liittyvistä argumenteista

    def test_maksettaessa_ostos_pankin_metodia_tilisiirto_kutsutaan_kelpaavalla_arvolla(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        # palautetaan aina arvo 42
        viitegeneraattori_mock.uusi.return_value = 42

        varasto_mock = Mock()

        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)

        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.tilimaksu("pekka", "12345")

        # varmistetaan, että metodia tilisiirto on kutsuttu
        pankki_mock.tilisiirto.assert_called_with("pekka",42,"12345","33333-44455",5)

    def test_maksettaessa_ostos_pankin_metodia_tilisiirto_kutsutaan_kelpaavalla_arvolla_kaksi_eri_tuotetta(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        # palautetaan aina arvo 42
        viitegeneraattori_mock.uusi.return_value = 42

        varasto_mock = Mock()

        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10
            if tuote_id == 2:
                return 3

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)
            if tuote_id == 2:
                return Tuote(2, "kalja", 4)

        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.lisaa_koriin(2)
        kauppa.tilimaksu("pekka", "12345")

        # varmistetaan, että metodia tilisiirto on kutsuttu
        pankki_mock.tilisiirto.assert_called_with("pekka",42,"12345","33333-44455",9)

    
    def test_maksettaessa_ostos_pankin_metodia_tilisiirto_kutsutaan_kelpaavalla_arvolla_kaksi_tuotetta_toista_ei_varastossa(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        # palautetaan aina arvo 42
        viitegeneraattori_mock.uusi.return_value = 42

        varasto_mock = Mock()

        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10
            if tuote_id == 2:
                return 0

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)


        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.lisaa_koriin(2)
        kauppa.tilimaksu("pekka", "12345")

        # varmistetaan, että metodia tilisiirto on kutsuttu
        pankki_mock.tilisiirto.assert_called_with("pekka",42,"12345","33333-44455",5)

    def test_maksettaessa_ostos_pankin_metodia_tilisiirto_kutsutaan_kelpaavalla_arvolla_kaksi_samaa_tuotetta(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        # palautetaan aina arvo 42
        viitegeneraattori_mock.uusi.return_value = 42

        varasto_mock = Mock()

        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)

        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.lisaa_koriin(1)
        kauppa.tilimaksu("pekka", "12345")

        # varmistetaan, että metodia tilisiirto on kutsuttu
        pankki_mock.tilisiirto.assert_called_with("pekka",42,"12345","33333-44455",10)

    def test_aloita_asiointi_nollaa_ostoksen_tiedot(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        # palautetaan aina arvo 42
        viitegeneraattori_mock.uusi.return_value = 42

        varasto_mock = Mock()

        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10
            if tuote_id == 2:
                return 5

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)
            if tuote_id == 2:
                return Tuote(2, "kalja", 20)

        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(2)
        kauppa.tilimaksu("pekka", "12345")


        # varmistetaan, että metodia tilisiirto on kutsuttu
        pankki_mock.tilisiirto.assert_called_with("pekka",42,"12345","33333-44455",20)

    def test_uusi_viitenro_joka_tapahtumalle(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        varasto_mock = Mock()

        viitegeneraattori_mock.uusi.side_effect = [42, 43]
        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10
            if tuote_id == 2:
                return 5

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)
            if tuote_id == 2:
                return Tuote(2, "kalja", 20)

        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.tilimaksu("pekka", "12345")
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(2)
        kauppa.tilimaksu("pekka", "12345")



        expected_calls = [
            call("pekka", 42, "12345", "33333-44455", 5),
            call("pekka", 43, "12345", "33333-44455", 20),
        ]

        pankki_mock.tilisiirto.assert_has_calls(expected_calls)
        assert viitegeneraattori_mock.uusi.call_count == 2

    def test_maksettaessa_ostos_pankin_metodia_tilisiirto_kutsutaan_kelpaavalla_arvolla_kun_poistettu_tuote(self):
        pankki_mock = Mock()
        viitegeneraattori_mock = Mock()

        # palautetaan aina arvo 42
        viitegeneraattori_mock.uusi.return_value = 42

        varasto_mock = Mock()

        # tehdään toteutus saldo-metodille
        def varasto_saldo(tuote_id):
            if tuote_id == 1:
                return 10
            if tuote_id == 2:
                return 10

        # tehdään toteutus hae_tuote-metodille
        def varasto_hae_tuote(tuote_id):
            if tuote_id == 1:
                return Tuote(1, "maito", 5)
            if tuote_id == 2:
                return Tuote(2, "kalja", 10)
        # otetaan toteutukset käyttöön
        varasto_mock.saldo.side_effect = varasto_saldo
        varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        # alustetaan kauppa
        kauppa = Kauppa(varasto_mock, pankki_mock, viitegeneraattori_mock)

        # tehdään ostokset
        kauppa.aloita_asiointi()
        kauppa.lisaa_koriin(1)
        kauppa.lisaa_koriin(2)
        kauppa.poista_korista(2)
        kauppa.tilimaksu("pekka", "12345")

        # varmistetaan, että metodia tilisiirto on kutsuttu
        pankki_mock.tilisiirto.assert_called_with("pekka",42,"12345","33333-44455",5)

def test_kirjanpito_lisaa_tapahtuma():
    kp = Kirjanpito()
    assert kp.tapahtumat == []

    kp.lisaa_tapahtuma("eka tapahtuma")
    kp.lisaa_tapahtuma("toka tapahtuma")

    assert kp.tapahtumat == ["eka tapahtuma", "toka tapahtuma"]


def test_tuote_hash_eq_str():
    t1 = Tuote(1, "Olut", 5)
    t2 = Tuote(1, "Olut eri nimi", 10)  # sama id -> pidetään samana tuotteena
    t3 = Tuote(2, "Siideri", 5)

    # __eq__
    assert t1 == t2
    assert t1 != t3

    # __hash__ – sama id -> sama hash
    assert hash(t1) == hash(t2)
    assert hash(t1) != hash(t3)

    # __str__
    assert str(t1) == "Olut"


def test_varasto_haku_saldo_ja_tapahtumat():
    # käytetään oikeaa kirjanpitoa, niin sen koodi tulee myös katettua
    kp = Kirjanpito()
    varasto = Varasto(kp)

    # hae_tuote – löytyvä id
    tuote = varasto.hae_tuote(1)
    assert isinstance(tuote, Tuote)
    assert tuote.id == 1

    # saldo käyttää hae_tuotea sisältä
    alku_saldo = varasto.saldo(1)
    assert alku_saldo > 0

    # hae_tuote – id jota ei ole -> None-haara
    assert varasto.hae_tuote(9999) is None

    # ota_varastosta vähentää saldoa ja kirjaa tapahtuman
    varasto.ota_varastosta(tuote)
    assert varasto.saldo(1) == alku_saldo - 1
    assert kp.tapahtumat[-1] == f"otettiin varastosta {tuote}"

    # palauta_varastoon nostaa saldoa ja kirjaa tapahtuman
    varasto.palauta_varastoon(tuote)
    assert varasto.saldo(1) == alku_saldo
    assert kp.tapahtumat[-1] == f"palautettiin varastoon {tuote}"


def test_viitegeneraattori_kasvattaa_viitetta():
    vg = Viitegeneraattori()

    first = vg.uusi()
    second = vg.uusi()
    third = vg.uusi()

    assert second == first + 1
    assert third == second + 1