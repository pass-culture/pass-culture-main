import { act, renderHook } from '@testing-library/react'

import { usePagination } from '@/commons/hooks/usePagination'

const itemsList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
const itemsPerPage = 3

describe('usePagination', () => {
  it('should paginate list', () => {
    const { result } = renderHook(() => usePagination(itemsList, itemsPerPage))

    expect(result.current.page).toBe(1)
    expect(result.current.pageCount).toBe(4)
    expect(result.current.currentPageItems).toEqual([1, 2, 3])

    act(() => {
      result.current.nextPage()
    })
    expect(result.current.currentPageItems).toEqual([4, 5, 6])

    act(() => {
      result.current.previousPage()
    })
    expect(result.current.currentPageItems).toEqual([1, 2, 3])

    act(() => {
      result.current.setPage(4)
    })
    expect(result.current.currentPageItems).toEqual([10])
  })
})
