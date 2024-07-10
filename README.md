# ml-5carddraw
Have a computer teach itself to play 5 card draw power.

## Files

| Filename | Description |
| --- | --- |  
| README.md | This file. |  
| 5card_table.pkl.gz | Card draw decision table (compressed) |
| 5card_odds.pkl.gz | 5-card draw odds table (compressed) |
| gzip_pkls.sh | (Bash) Compresses all *.pkl files in the directory. |
| ungzip_pkls.sh | (Bash) Decompresses all gzipped files in the directory. |
| 5-card-draw_65.py | Creates the draw decision table. Script ends after the table achieves a 65%+ hand improvement rate. |
| 5-card-draw_inf.py | Creates the draw decision table. Runs indefinitely. |
| 5-card-draw_2p.py | Creates the odds table. |
