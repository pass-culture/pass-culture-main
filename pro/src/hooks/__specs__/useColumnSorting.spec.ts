import { act, renderHook } from '@testing-library/react'

import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'

enum SomeColumns {
  COLUMN_1 = 'column1',
  COLUMN_2 = 'column2',
  COLUMN_3 = 'column3',
}

describe('useColumnSorting', () => {
  it('should change sorting mode on callback call', async () => {
    const { result } = renderHook(() => useColumnSorting<SomeColumns>())

    expect(result.current.currentSortingColumn).toBeNull()
    expect(result.current.currentSortingMode).toBe(SortingMode.NONE)

    act(() => {
      result.current.onColumnHeaderClick(SomeColumns.COLUMN_2)
    })
    expect(result.current.currentSortingColumn).toBe(SomeColumns.COLUMN_2)
    expect(result.current.currentSortingMode).toBe(SortingMode.ASC)

    act(() => {
      result.current.onColumnHeaderClick(SomeColumns.COLUMN_2)
    })
    expect(result.current.currentSortingColumn).toBe(SomeColumns.COLUMN_2)
    expect(result.current.currentSortingMode).toBe(SortingMode.DESC)

    act(() => {
      result.current.onColumnHeaderClick(SomeColumns.COLUMN_2)
    })
    expect(result.current.currentSortingColumn).toBe(SomeColumns.COLUMN_2)
    expect(result.current.currentSortingMode).toBe(SortingMode.NONE)

    act(() => {
      result.current.onColumnHeaderClick(SomeColumns.COLUMN_2)
    })
    expect(result.current.currentSortingColumn).toBe(SomeColumns.COLUMN_2)
    expect(result.current.currentSortingMode).toBe(SortingMode.ASC)
  })
})
