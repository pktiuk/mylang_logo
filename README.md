# TKOM - Język zbliżony do logo z elementami obiektowymi

**Paweł Kotiuk 292898**
## Opis projektu

Stworzenie własnego interpretera języka koncepcyjnie zbliżonego do Logo, lecz z mechanizmami obiektowymi w kontekście żółwia. Ma on pozwalać min na tworzenie wielu instancji żółwia na ekranie.  
Język Logo znany w Polsce także jako Logomocja. Jest on prostym językiem programowania skierowanym głównie do uczniów szkół. Pozwala on w sposób wizualny zapoznać się uczniom z programowaniem. W tym wypadku aspekt ten realizowany poprzez pozwolenie użytkownikowi na sterowanie kursorem (żółwiem) rysującym po planszy za pomocą odpowiednich komend.

## Funkcjonalność

Cechy samego języka:

- Język skryptowy mogący działać w trakcie wpisywania
- Lokalność zmiennych
- Typy wbudowane
  - num - liczba
  - string
  - turtle - jest to obiekt reprezentujący wskaźnik (domyślnie będący żółwiem), którym kierować może użytkownik
  - bool
  - None
- dynamiczne typowanie zmiennych
- Wykonywanie wyrażeń arytmetycznych działający zgodnie z ogólnie przyjętą dot. konwencją kolejności operatorów.
- Wykonywanie wyrażeń logicznych działający zgodnie z ogólnie przyjętą dot. konwencją kolejności operatorów.
- Możliwe istnienie wielu instancji żółwia jednocześnie
- Definiowanie własnych funkcji oraz ich późniejsze używanie
- Możliwość tworzenia pętli
- Instrukcje warunkowe `if`
- Obsługa niektórych sytuacji wyjątkowych (np. dzielenie przez 0)
- Funkcja print wypisująca informacje

Pozostałe wymagania dotyczące funkcjonalności:

- wbudowany obiekt żółwia
- stworzenie GUI wizualizującego ruchy oraz linie rysowane przez żółwia.

## Realizacja

Projekt zostanie napisany w języku python, zaś samo GUI będzie stworzone z wykorzystaniem biblioteki QT.

Okno główne będzie najpewniej podzielone na 3 główne części:

- wizualizacja - będzie ono pokazywało utworzony obrazek
- konsola - miejsce, gdzie będą wypisywane komunikaty oraz wiadomości
- pole tekstowe - miejsce gdzie będzie wpisywany kod. W tym miejscu użytkownik będzie także informowany o wszelkich problemach i wyjątkach

## Składania

Typ wbudowany `Turtle` będzie zawierał metody odpowiadające metodom, które w oryginalnym logo służyły do rysowania (`pd` - pen down, `fd` - forward `rt` - right turn etc.).

Przykładowy program rysujący kwadrat:

```cpp
// Najpierw definiujemy potrzebną nam funkcję, następnie można od razu ją wykonać.

fun draw_square(len)
{
  i = 0
  t = Turtle()
  while(i<=3)
  {
    t.fd(len)
    t.rt(90)
    i=i+1
  }
  pole = len*len
  return(pole)
}// Na ekranie pojawi się nowy żółw, narysuje kwadrat i po tym powinien zniknąć

print("Obrysowane pole ")

pole=draw_square(10);

msg = ""

if(pole > 10 && pole <200)
{
  print("jest wieksze od 10 i mniejsze od 200")
}else
{
  print("jest inne niz przewidywane")
}

```

W konsoli powinno zostać wypisane `Obrysowane pole jest wieksze od 10 i mniejsze od 200`.

## Gramatyka

**program**  =  `{ statement | definition };`  
**definition** = `functionDefinition;`  
**functionDefinition** =  `"fun" identifier, "(", [ identifier, {",", identifier} ], ")", block;`  
**statement** = ` ifStatement | whileStatement | expression | valueAssignment; `  
**ifStatement** = `"if", "(", logicalExpression, ")", block[ "else" block] ;`  
**whileStatement** = `"while", "(", logicalExpression, ")", block;`  
**block** = `"{", {statement}, "}" ;`  

**valueAssignment** = `identifier, "=", expression;`  
**expression** = `logicalExpression | mathExpression;`  
**logicalExpression** = `andCondition, {"||", andCondition};`  
**andCondition** = `relation, {"&&", relation};`  
**relation** = `mathExpression, [compSign, mathExpression] | "(" logicalExpression ")"`;  
**mathExpression** = `mathExpression, addOperator | factor, {multOperator};`  
**factor** = `value | "(" mathExpression ")";`  
**value** = `[ "!" | "-" ], identifier, {functionOperator | fieldOperator } | [ "!" | "-" ], constValue`  

**addOperator** = `addSign, mathExpression;`  
**multOperator** = `multSign, factor;`  
**functionOperator** = `"(" [ expression, {",", expression} ], ")";`  
**fieldOperator** = `"." identifier`

**addSign** = `"+" | "-" ;`  
**multSign** = `"*" | "/";`  
**logicSign** = `"||" | "&&";`  
**compSign** = `"==" | "!=" | "<" | "<=" | ">" | ">=";`  

**identifier** = `letter, {naturalNumber | letter | specialSign};`  
**constValue** = `number | string;`  
**string** = `'"' {letter | naturalNumber | specialSign | stringEscapedSign} '"';`  
**number** = `naturalNumber [ ".", digit, {digit}];`  
**naturalNumber** = `"0" | (nonZeroDigit, {digit});`  

**letter** = `"A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" ;`  
**nonZeroDigit** = `"1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;`  
**digit** = `"0" | nonZeroDigit;`  
**specialSign** = `"_";`  
**stringEscapedSign** = `'/"';`  

## Tokeny

Lista tokenów:

identifier - token zawierający identyfikator, który może wskazywać na jakąś zmienną, czy też funkcję  
constValue - token bezpośrednio przeliczany na jakąś wartość  
"fun", "if", "else", "while",  
"{", "}", "(", ")", '"'  
"+", "-", "*",  "/", "!"  "="  
"||", "&&", "==",  "!=", "<", "<=", ">", ">="  
EOF - End Of File  
EOL - End Of Line

Funkcje wbudowane takie jak `print` nie będą tokenami, podobnie jak nazwy typów wbudowanych, bedą one rozpoznawane jako identyfikatory.

## Testy

Testy poszczególnych elementów analizatora są realizowane za pomocą prostych testów jednostkowych stworzonych z pomocą narzędzia pytest.  

Uruchomienie testów:

```bash
pytest --pyargs tkom_logo
```

Poszczególne moduły systemu są testowane oddzielnie, aby umożliwić łatwiejszą weryfikację testów.  
Testy są pisane na bieżąco, przy każdym znalezionym błędzie, który nie jest pokryty w ramach zbioru testowego dodawany jest nowy testcase mający badać dany przypadek.
