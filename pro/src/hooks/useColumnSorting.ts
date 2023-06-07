import { useCallback, useState } from 'react'

export enum SortingMode {
  ASC = 'asc',
  DESC = 'desc',
  NONE = 'none',
}

export const useColumnSorting = <SortingColumn>() => {
  const [currentSortingColumn, setCurrentSortingColumn] =
    useState<SortingColumn | null>(null)
  const [currentSortingMode, setCurrentSortingMode] = useState<SortingMode>(
    SortingMode.NONE
  )

  const onColumnHeaderClick = useCallback(
    (headerName: SortingColumn) => {
      if (currentSortingColumn !== headerName) {
        setCurrentSortingColumn(headerName)
        setCurrentSortingMode(SortingMode.ASC)
        return
      } else {
        if (currentSortingMode === SortingMode.ASC) {
          setCurrentSortingMode(SortingMode.DESC)
        } else if (currentSortingMode === SortingMode.DESC) {
          setCurrentSortingMode(SortingMode.NONE)
        } else {
          setCurrentSortingMode(SortingMode.ASC)
        }
      }
    },
    [currentSortingColumn, currentSortingMode]
  )

  return { currentSortingColumn, currentSortingMode, onColumnHeaderClick }
}

export const sortColumnByDateString = <
  DateColumn extends string,
  Items extends { [key in DateColumn]: string }
>(
  items: Items[],
  column: DateColumn,
  sortingMode: SortingMode
): Items[] =>
  items.sort(
    (a, b) =>
      (Date.parse(a[column]) - Date.parse(b[column])) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
  )

export const sortColumnByDateObject = <
  DateColumn extends string,
  Items extends { [key in DateColumn]: Date | null | '' }
>(
  items: Items[],
  column: DateColumn,
  sortingMode: SortingMode
): Items[] =>
  items.sort((a, b) => {
    const dateA = a[column]
    const dateB = b[column]

    if (dateA === null || dateA === '') {
      return -1
    }

    if (dateB === null || dateB === '') {
      return 1
    }

    return (
      (dateA.getTime() - dateB.getTime()) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
    )
  })

export const sortColumnByNumber = <
  NumberColumn extends string,
  Items extends { [key in NumberColumn]: number | null | '' }
>(
  items: Items[],
  column: NumberColumn,
  sortingMode: SortingMode
): Items[] =>
  items.sort((a, b) => {
    const valueA = a[column]
    const valueB = b[column]

    const notNullValueA: number =
      (valueA === '' ? null : valueA) ?? Number.MAX_VALUE
    const notNullValueB: number =
      (valueB === '' ? null : valueB) ?? Number.MAX_VALUE

    return (
      (notNullValueA - notNullValueB) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
    )
  })
