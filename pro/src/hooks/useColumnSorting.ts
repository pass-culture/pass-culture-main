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
