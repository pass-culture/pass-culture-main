import { act, renderHook } from '@testing-library/react'

import {
  SortingMode,
  useColumnSorting,
  sortColumnByDateString,
  sortColumnByDateObject,
  sortColumnByNumber,
} from 'hooks/useColumnSorting'

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

describe('sortColumnByDateString', () => {
  it('should sort by date string', () => {
    expect(
      sortColumnByDateString(
        [
          { [SomeColumns.COLUMN_1]: '2021-01-01' },
          { [SomeColumns.COLUMN_1]: '2019-01-01' },
          { [SomeColumns.COLUMN_1]: '2020-01-01' },
        ],
        SomeColumns.COLUMN_1,
        SortingMode.ASC
      )
    ).toEqual([
      { [SomeColumns.COLUMN_1]: '2019-01-01' },
      { [SomeColumns.COLUMN_1]: '2020-01-01' },
      { [SomeColumns.COLUMN_1]: '2021-01-01' },
    ])
  })
})

describe('sortColumnByDateObject', () => {
  it('should sort by date object', () => {
    expect(
      sortColumnByDateObject(
        [
          { [SomeColumns.COLUMN_1]: new Date('2021-01-01') },
          { [SomeColumns.COLUMN_1]: '' },
          { [SomeColumns.COLUMN_1]: null },
          { [SomeColumns.COLUMN_1]: new Date('2019-01-01') },
        ],
        SomeColumns.COLUMN_1,
        SortingMode.ASC
      )
    ).toEqual([
      { [SomeColumns.COLUMN_1]: null },
      { [SomeColumns.COLUMN_1]: '' },
      { [SomeColumns.COLUMN_1]: new Date('2019-01-01') },
      { [SomeColumns.COLUMN_1]: new Date('2021-01-01') },
    ])
  })
})

describe('sortColumnByNumber', () => {
  it('should sort by number', () => {
    expect(
      sortColumnByNumber(
        [
          { [SomeColumns.COLUMN_1]: 3 },
          { [SomeColumns.COLUMN_1]: '' },
          { [SomeColumns.COLUMN_1]: null },
          { [SomeColumns.COLUMN_1]: 1 },
        ],
        SomeColumns.COLUMN_1,
        SortingMode.ASC
      )
    ).toEqual([
      { [SomeColumns.COLUMN_1]: 1 },
      { [SomeColumns.COLUMN_1]: 3 },
      { [SomeColumns.COLUMN_1]: '' },
      { [SomeColumns.COLUMN_1]: null },
    ])
  })
})
