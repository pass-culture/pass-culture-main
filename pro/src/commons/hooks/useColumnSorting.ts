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
        return SortingMode.ASC
      } else {
        if (currentSortingMode === SortingMode.ASC) {
          setCurrentSortingMode(SortingMode.DESC)
          return SortingMode.DESC
        } else if (currentSortingMode === SortingMode.DESC) {
          setCurrentSortingMode(SortingMode.NONE)
          return SortingMode.NONE
        } else {
          setCurrentSortingMode(SortingMode.ASC)
          return SortingMode.ASC
        }
      }
    },
    [currentSortingColumn, currentSortingMode]
  )

  return { currentSortingColumn, currentSortingMode, onColumnHeaderClick }
}

export function giveSortingModeForAlly(sortingMode: SortingMode): string {
  switch (sortingMode) {
    case SortingMode.ASC:
      return 'ascendant'
    case SortingMode.DESC:
      return 'descendant'
    case SortingMode.NONE:
      return 'par défaut'
  }
}
