import { useCallback, useState } from 'react'

import { type EnumType } from 'commons/custom_types/utils'

export const SortingMode = {
  ASC: 'asc',
  DESC: 'desc',
  NONE: 'none',
} as const
// eslint-disable-next-line no-redeclare
export type SortingMode = EnumType<typeof SortingMode>

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
