# TKOM - Obiektowy język zbliżony do logo

## Opis projektu

Stworzenie własnego interpretera języka koncepcyjnie zbliżonego do Logo, lecz z mechanizmami obiektowymi.  
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

- wizualizacja - będzie ono pokazywało utworzony obrazel
- konsola - miejsce, gdzie będą wypisywane komunikaty oraz wiadomości
- pole tekstowe - miejsce gdzie będzie wpisywany kod

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
}// Na ekranie pojawi się nowy żółw, narysuje nowy kwadrat i po tym powinien zniknąć

draw_square(10);
```

## Gramatyka

**program**  =  `{ statement | definition };`  
**definition** = `classDefinition | functionDefinition | variableDefinition;`  
**classDefinition**   = `"class", identifier, "{", { variableDefinition | functionDefinition }, "}";`  
**functionDefinition** =  `"fun" identifier, "(", [ {identifier, identifier, ","}, identifier, identifier ], ")", "{", {statement}, "}" ;`  
**variableDefinition** = `identifier, identifier, [ = expression ] ;`  
**statement** = ` [ ifStatement | whileStatement | expression | valueAssignment ] ; `  
**ifStatement** = `"if", "(", expression, ")", "{", {statement}, "}" ;`  
**whileStatement** = `"while", "(", expression, ")", "{", {statement}, "}" ;`  

**valueAssignment** = `identifier, "=", expression;`  
**expression** = `( "(", expression, ")" ) | (identifier, {operator}) | number | string;`  

**operator** = `mathOperator | logicOperator | functionOperator | fieldOperator;`  
**mathOperator** = `mathSign, expression;`  
**mathSign** = `"+" | "-" | "*" | "/";`  
**logicOperator** = `logicSign, expression;`  
**logicSign** = `"==" | "!=" | "<" | "<=" | ">" | ">=" | "||" | "&&";`  
**functionOperator** = `"(" [ {expression, ","}, expression ], ")";`  
**fieldOperator** = `".", identifier;`  

**identifier** = `letter, {number , letter, specialSign};`  
**specialSign** = `"_" | "-" ;`  
**letter** = `"A" .. "Z" | "a" .. "z";`  
**number** = `"0" | (("1" .. "9"), {"0" .. "9"});`  
**string** = `'"' {letter | number | specialSign } '"';`

## Słowa kluczowe

Lista słów kluczowych:

Turtle  
if while return fun  
print