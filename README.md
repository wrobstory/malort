# Malort

### JSON -> Column Types

Malort is a tool for taking somewhat structured JSON data and trying to sniff out the appropriate relational db column types from the keys and values. It currently only supports Redshift, but the column mappers can be easily extended to other DBs.

Why
-----
Because for semi-structured documents where the schema will rarely change, we'd rather have the speed and familiar query-ability of structured table columns rather than dumping the JSON blob in a single column.

How
------
Malort will read through a directory of .json files or flat text files with delimited JSON blobs and generate relevant statistics on each key.

For example, let's look at a directory with two JSON files, and one text file with newline JSON:
```json
{"intfield": 5,
 "floatfield": 2.345,
 "charfield": "fixedlength",
 "varcharfield": "var"}

 {"intfield": 10,
 "floatfield": 4.7891,
 "charfield": "fixedlength",
 "varcharfield": "varyin"}
 ```

 ```
{"intfield": 15,"floatfield": 3.0012,"charfield": "fixedlength","varcharfield": "varyingle"}
{"intfield": 20,"floatfield": 10.8392,"charfield": "fixedlength","varcharfield": "varyinglengt"}
```

Malort will calculate relevant statistics:
```python
>>> import malort as mt
>>> result = mt.analyze('dir', delimiter='\n')
>>> result.stats
{'charfield': {'str': {'count': 4,
                       'max': 11,
                       'mean': 11.0,
                       'min': 11,
                       'sample': ['fixedlength',
                                  'fixedlength',
                                  'fixedlength']}},
 'floatfield': {'float': {'count': 4,
                          'fixed_length': False,
                          'max': 10.8392,
                          'max_precision': 6,
                          'max_scale': 4,
                          'mean': 5.243,
                          'min': 2.345}},
 'intfield': {'int': {'count': 4, 'max': 20, 'mean': 12.5, 'min': 5}},
 'varcharfield': {'str': {'count': 4,
                          'max': 12,
                          'mean': 7.5,
                          'min': 3,
                          'sample': ['varyin', 'varyingle', 'varyinglengt']}}}
```

Malort has determined the type(s) for each key, as well as relevant statistics for that type. Malort can then be used to guess the Redshift column types:

```python
>>> result.get_redshift_types()
{'intfield': 'SMALLINT',
 'floatfield': 'REAL',
 'varcharfield': 'varchar(12)',
 'charfield': 'char(11)'}
 ```

Malort supports the ability to print the entire result as a Pandas DataFrame:
```python
>>> result.to_dataframe()
            key  count   type    mean      max     min  max_precision  max_scale fixed_length                                   sample redshift_types
0      intfield      4    int  12.500  20.0000   5.000            NaN        NaN         None                                     None       SMALLINT
1    floatfield      4  float   5.243  10.8392   2.345              6          4        False                                     None           REAL
2  varcharfield      4    str   7.500  12.0000   3.000            NaN        NaN         None        [varyin, varyingle, varyinglengt]    varchar(12)
3     charfield      4    str  11.000  11.0000  11.000            NaN        NaN         None  [fixedlength, fixedlength, fixedlength]       char(11)
```

Why is it named Malort?
-----------------------
Because this is kind of a distasteful thing to do.

Couldn't I have done this with sed/awk/xargs/mapreduce?
-------------------------------------------------------
Yes.
