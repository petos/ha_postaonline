# PostaOnline

Integrace pro Home Assistant umožňující sledování zásilek České pošty prostřednictvím služby PostaOnline.

Každá sledovaná zásilka je v Home Assistantu reprezentována jako jedno zařízení (Device) obsahující několik senzorů.

## Funkce

- Sledování zásilek České pošty podle podacího čísla
- Automatická aktualizace stavu zásilky
- Každá zásilka je vytvořena jako samostatné zařízení
- Status zásilky je poskytován jako `enum` senzor vhodný pro automatizace
- Zobrazení místa poslední události

## Instalace
- Přes HACS

  [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/ha_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Petos&repository=ha_postaonline)

  - Nainstalujte HACS
  - V HACS rozhraní kliknout v pravém horním rohu na tři svislé tečky
  - Kliknout na Vlastní repozitáře
  - Přidat adresu `https://github.com/petos/ha_postaonline` a typ `Integrace`
  - Po přidání repozitáře vyhledat `PostaOnline` a nainstalovat
  - Po restartu Home Assistenta přidat jako Integraci v Nastavení -> Integrace
- Ručně:
  - Nahrajte obsah `custom_components/ha_postaonline/` do `/config/custom_components/ha_postaonline/`
## Konfigurace

Při přidávání integrace jsou zadávány následující údaje:

| Položka | Povinné | Popis |
|---------|:-------:|-------|
| Tracking number | ✔ | Podací číslo zásilky České pošty |
| Description | | Volitelný popis zásilky. Použije se jako název zařízení v Home Assistantu. |

---

## Senzory

| Senzor | Popis |
|--------|-------|
| Status | Aktuální stav zásilky |
| Location | Místo poslední události |

### Status

Status je implementován jako `enum` senzor.

Možné hodnoty:

- `preparing_to_delivery`
- `now_delivering`
- `in_transit`
- `delivered`
- `unknown`

To umožňuje snadné vytváření automatizací bez závislosti na přesném textu vraceném Českou poštou.

Příklad automatizace:

```yaml
condition:
  - condition: state
    entity_id: sensor.balik_status
    state: delivered
```

### Atributy

Status senzor poskytuje také následující atributy:

| Atribut | Popis |
|---------|-------|
| tracking_number | Podací číslo |
| event_date | Datum poslední události |
| zip | PSČ |
| raw_status | Původní text stavu vrácený Českou poštou |

---

## Poznámky

- Integrace využívá veřejně dostupnou službu PostaOnline.
- Aktualizace probíhá v nastaveném intervalu.
- Interní enum stavy jsou stabilní a nezávislé na změnách formulací na webu České pošty.

---


## Hlášení chyb
Nejlépe přes https://github.com/petos/ha_postaonline/issues
