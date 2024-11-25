# HTML Fragmentation

## Task description

Look at [data/task.pdf](./data/task.pdf)

__Note__: _solution don't except any props for splitable tags_
__Note__: _validation of source html fragment is out of scope_

## How to run

```bash
python split_msg.py --max-len=3072 ./data/source.html
```

## How to run tests

```bash
python tests.py
```

## Repository description

### Root folder

Root folder contains `split_msg.py` and `tests.py` scripts and folders `data` and `msg_split`

- `split_msg.py` - is the main script. See [How to run](## How to run)
- `test.py` contains unit tests. See [How to run test](## How to run tests)
- `data` folder contains task description and demo source file `source.html`
- `msg_split` folder is a python module with implemetation of solution

### msg_split module

- `const.py` - valuable constants
- `exceptions.py` - user defined exceptions for solution
- `models.py` - dataclasses for representation of internal state of solution
- `parser.py` - contains child class of `HTMLParser` wich use for parsing source data
- `split_algo.py` - algorithm of HTML fragmentation

## HTML Fragmetation process

Fundamental idea is map source HTML to correct brackets sequence. Then just split original sequence to fragments less than `max_len`. Splitted fragments must be correct bracket sequences too.

1. First of the all, source data splitted by _chunks_
    1. Some _chunks_ are _brackets_
    1. _bracket_ can be open bracket or close bracket
    1. Not _bracket_ _chunks_ are unsplitable parts
    1. Every _chunk_ provide info about his position in source.
    1. Every _bracket_ provide info about his original tag
2. Next step is going through chunks sequence and maintain: (full length of fragment - `full_len`, sum of paired (open+close tag) length of opened _brackets_ - `pure_len`, _chunk_ length - `chunk_len`)
    1. If `chunk_len` or `pure_len` is greater than `max_len` - __splitting is impossible__
    2. Otherwise if `full_len` will be greater than `max_len` after add next _chunk_ - fragmentate and try again
    3. Else - add _chunk_ to consideration part
3. When processed all _chunks_ sequence, may remains  some untagged content
    1. In that case - just splitting that content to fragments without additions

## Estimates

Calculation complexity of solution `O(n*m)` where n - length of data source, m - `max_len`
