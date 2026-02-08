## scan result
```
folder -> { folders with common files }
folder -> { file check sums }
check sum  -> file name

step 1: collect all file objects with same name
file name -> objects
filter out entries with less than 2 objects

go through file objects
separate into files sizes


```
## analysis of scan result
generate:
-   hash:
    -   folder from dirnames of file entry
    -   files contained (set)
Scan result should be a listing of folder common files
-   hash:
    -   hash of folders involved
        folders involved

## implementation
### hash of folders involved
