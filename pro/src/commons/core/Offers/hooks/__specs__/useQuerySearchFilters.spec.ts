import { renderHook } from '@testing-library/react'
import * as reactRouter from 'react-router'

import { useQueryCollectiveSearchFilters } from '../useQuerySearchFilters'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: vi.fn(),
}))

describe('useQueryCollectiveSearchFilters', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return status as an array if status is a string in the URL', () => {
    // @ts-expect-error
    reactRouter.useLocation.mockReturnValue({
      search: '?status=UNDER_REVIEW&page=2',
    })

    const { result } = renderHook(() => useQueryCollectiveSearchFilters())
    expect(result.current.status).toEqual(['UNDER_REVIEW'])
    expect(result.current.page).toBe(2)
  })

  it('should return status as an array if multiple status are present in the URL', () => {
    // @ts-expect-error
    reactRouter.useLocation.mockReturnValue({
      search: '?status=active&status=en-attente',
    })

    const { result } = renderHook(() => useQueryCollectiveSearchFilters())
    expect(result.current.status).toEqual(['PUBLISHED', 'UNDER_REVIEW'])
  })

  it('should return undefined for status if status is absent in the URL', () => {
    // @ts-expect-error
    reactRouter.useLocation.mockReturnValue({
      search: '',
    })

    const { result } = renderHook(() => useQueryCollectiveSearchFilters())
    expect(result.current.status).toBeUndefined()
  })

  it('should convert page to a number', () => {
    // @ts-expect-error
    reactRouter.useLocation.mockReturnValue({
      search: '?page=3',
    })

    const { result } = renderHook(() => useQueryCollectiveSearchFilters())
    expect(result.current.page).toBe(3)
  })
})
