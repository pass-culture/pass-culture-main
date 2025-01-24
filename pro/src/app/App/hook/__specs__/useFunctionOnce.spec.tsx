import { renderHook } from '@testing-library/react'

import { useFunctionOnce } from '../useFunctionOnce'

const callBackFn = vi.fn()

describe('useFunctionOnce()', () => {
  it('should only call callback function once', () => {
    const { result } = renderHook(() => useFunctionOnce(callBackFn))
    result.current()

    expect(callBackFn).toHaveBeenCalledTimes(1)

    result.current()

    expect(callBackFn).toHaveBeenCalledTimes(1)
  })
})
