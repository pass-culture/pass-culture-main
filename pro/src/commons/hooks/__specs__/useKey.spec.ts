import { act, renderHook } from '@testing-library/react'

import { useKey } from '../useKey'

describe('useKey()', () => {
  it('should start with a zero value', () => {
    const { result } = renderHook(() => useKey())

    expect(result.current.value).toBe(0)
  })

  it('should increment the value on update', () => {
    const { result } = renderHook(() => useKey())

    act(() => {
      result.current.update()
    })

    expect(result.current.value).toBe(1)
  })

  it('should increment once per update call, even within the same render cycle', () => {
    const { result } = renderHook(() => useKey())

    act(() => {
      result.current.update()
      result.current.update()
    })

    expect(result.current.value).toBe(2)
  })
})
