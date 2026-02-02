# rename tracks by EAC database info
## original info by EAC
```
CD: Xploding Plastix - Amateur Girlfriends Go Proskirt Agents
      Info URL: https://www.amazon.co.uk/gp/product/B00005BIHK
      Barcode: 7035538881886
      Release date: 2001-03-12
      Release country: NO
      Release label: Beatservice Records
      Release catalog#: BSCD038


01. Sports, Not Heavy Crime    [0:05:09.08]
02. Funnybones & Lazylegs    [0:04:50.24]
03. 6‐Hours Starlight    [0:03:24.15]
04. Behind the Eightball    [0:04:51.54]
05. Single Stroke Ruffs    [0:02:30.04]
06. Treat Me Mean, I Need the Reputation    [0:05:00.16]
07. Relieved Beyond Repair    [0:01:47.37]
08. Tintinnamputation    [0:04:28.31]
09. More Powah to Yah    [0:05:28.64]
10. Having Smarter Babies    [0:04:59.20]
11. Far‐Flung Tonic    [0:04:53.45]
12. Happy Jizz Girls    [0:02:56.05]
13. Doubletalk Gets Through to You    [0:05:25.57]
14. Comatose Luck    [0:03:39.57]
```
## applied regexes
regex1: `^(\d\d)\.(.*)[ \t]*\[(?:\d{1,2}[:.]?)+\]$`

-> $1 is number $2 is new Title

## file search regex(es)
regex1: `^(\d\d) Track\1.(wav|mp3)$`

-> $1 is number $2 is extension

regex2: `^info.txt$`
