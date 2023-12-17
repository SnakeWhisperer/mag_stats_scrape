```
C:\..>cd <directorio> 
C:\..>python
```

```python
from stats34 import scrape, dump_stats, dump_player, csv_dump

today = scrape(teams=['mag', 'mar'])
log = dump_stats(today)

dump_player(today, '<id>')
```
