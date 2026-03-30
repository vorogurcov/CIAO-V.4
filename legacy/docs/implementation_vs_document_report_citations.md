# Привязка пунктов анализа к топикам статьи

Формат «ссылки» в DOCX: указываю *Listing / Table / Figure* и краткое название того фрагмента, который использовался в моём сравнении.

## P0. Нет полноценного параллельного запуска автоматов

- `Listing 5. Description of the CIAO v.3 language interpreter using stepwise refinement method` — алгоритм, основанный на обработке событий через очередь (`initQ/putQ/isReadyQ/moveQ/getQ`), где каждый шаг обработки отделён.
- `Listing 3. Event queue methods` — явные операции очереди (`initQ`, `isReadyQ`, `putQ`, `moveQ`, `getQ`).
- `Fig. 1. Dispatcher and Queue automaton object diagrams with connection scheme` — разбиение на диспетчер (Dispatcher) и очередь (Queue) как отдельные автомата/роли.

## P0. Архитектура интерпретатора не соответствует Dispatcher/Queue/Handler/Storage

- `Fig. 1` — диспетчер + очередь как отдельные компоненты.
- `Fig. 2. Handler and Storage automaton object diagrams with connection scheme` — выделение ролей `Handler` (обработка одного шага события) и `Storage` (хранилище внутреннего представления).
- `Listing 4. Internal representation access methods` — ожидание, что доступ к внутренней модели будет оформлен набором методов (идея separation of concerns).

## P1. Вместо очереди событий используется рекурсивная диспетчеризация

- `Listing 5` — последовательный цикл обработки событий через очередь (а не рекурсивное «сразу интерпретировать»).
- `Listing 3` — семантика очереди как базового механизма, через который должны проходить новые события.
- `Listing 2. Event storage structure` — событие как самостоятельная сущность, которую нужно ставить в очередь.

## P1. Ограничение на двусвязные (бинарные) связи

- `Listing 1. Internal representation of program in CIAO v.3 language` — модель интерфейса:
  - `Interface = struct { ... link : struct { a : name , p : name } }`
  - то есть связь интерфейса описывает (а) имя связанного автомата и (b) имя предоставленного интерфейса — по сути бинарное связывание интерфейсов на уровне метамодели.
- Раздел сразу после `Listing 1` (про compile-time constant computation):
  - «connection scheme … processed immediately during compilation (parsing) and embedded into the transition’s internal representation»  
  - это поддерживает идею, что маршрутизация эффектов/вызовов в runtime идёт по заранее закреплённым (a, p/e) отношениям.

## P2. Частичное несовпадение с event-driven паттерном и `tick`

- Таблица и текст про `tick`:
  - `Table 1. Implementation patterns for imperative constructs in automata programs` — в паттернах для циклов используется event `tick`.
- Абзац про исключение completion transitions в CIAO v.3:
  - «completion transitions have been excluded … consequently, all transitions in CIAO v.3 are strictly event-driven»
  - «an event called tick is introduced … automaton object self-generates this event».

## Отдельно про изображения (Fig. 1 / Fig. 2)

- `Fig. 1` — используется для обоснования ожидания наличия отдельной роли `Dispatcher` и механизма queue-based диспетчеризации.
- `Fig. 2` — используется для обоснования ожидания отдельной роли `Handler` и `Storage`, и того, что обработка событий должна быть «шаговой», а не рекурсивной.

## Ограничение по «вплоть до картинок»

- В текущем сравнении я опирался на подписи/контекст вокруг фигур и на то, что в документе явно указаны `Fig. 1` и `Fig. 2` с нужными ролями.
- Полное OCR-пиксельное распознавание содержимого диаграмм (без подписей) в моём окружении не было доступно.

