# Téma zápočtového programu

+ Aplikace v Pythonu postavená na frameworku FastAPI bude sloužit jako generátor faktur s templatingem v Jinja2. Bude obsahovat databázi uživatelů s autentizačním mechanismem a úložiště faktur ve formě souborů.
+ Uživatelé budou moci vytvářet nové faktury, mazat existující a přiřazovat k nim štítky. Aplikace umožní i zpětné zobrazení dříve uložených faktur.

# Specifikace programu

## 1. Popis a zaměření programu

- Jedná se o program na generování faktur pomocí webového rozhraní.

- Výstup programu (faktura) bude ve formátu PDF kterou si člověk bude moci stáhnout.

- Systémy na generování faktur jsou často složité na ovládání a placené. V případě AI je spíše překážka správné formátování souboru a layout.
------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 2. Popis funkcionality

### 2.1. Funkce 1

**Autentizace a autorizace** uživatelů a držení session na straně serveru / počítače na kterém je systém hostovaný.

### 2.2. Funkce 2

**Vytvoření položek faktury** pomocí HTML/JS formuláře s POST-enpointem ve FastAPI.

### 2.3 Funkce 3

**Uložení a mazání faktury** v rozhraní uživatele

### 2.4 Funkce 4

**Přiřazení štítku k faktuře** v rozhraní uživatele

### 2.5 Funkce 5

**Export faktury** v rozhraní uživatele

---

## 3. Uživatelské rozhraní, vstupy a výstupy

### 3.1. Obrazovky

#### 3.1.1. Obrazovka 1

Registration page, na které člověk vytvoří přihlašovací údaje. Tvorba v HTML, JS, Bootstrap.

#### 3.1.2. Obrazovka 2

Login page, na které se člověk může přihlásti ke svému účtu.

#### 3.1.3. Obrazovka 3

Invoice Form, na které se člověk upravuje html formulář s informacemi o firmě, ceně atd.

#### 3.1.4. Obrazovka 4

User page, kde člověk provádí akce jako mazání, export, šťítkování ...
---------------------------------------------------------------------------------

## 4. Použité technologie

#### 4.1 Frontend

HTML, JAVASCRIPT, BOOTSTRAP

#### 4.2 Backend

FastAPI, Jinja, Redis, SQL, Uvicorn
-----------------------------------

## 5. Odkazy (Reference)

- Dokumentace FastAPI https://fastapi.tiangolo.com/
- Bootstrap Docs
- Youtube
- W3schools
- geeksforgeeks.com
- Reddit
- Google

---

## 6. Použití AI

Prohlašuji že z morálních a etických důvodů nikdy při tvorbě nepoužiju AI.

Nevím zda je vůbec povolená, nicméně ji nepoužiji.
