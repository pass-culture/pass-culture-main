.results[].hits
| map(. + .offer
    | del(.offer,.venue,.offerer,._highlightResult)
)
| (map(keys) 
    | add 
    | unique
) as $cols
| map(. as $row
    | $cols
    | map($row[.])
) as $rows
| $cols, $rows[]
| @csv