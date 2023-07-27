import { renderHook, waitFor } from '@testing-library/react'

import { useAdapter } from '..'

interface SuccessPayload {
  success: string
}
interface FailurePayload {
  error: string
}
type TestingAdapter = Adapter<void, SuccessPayload, FailurePayload>

const getTestingAdapter = (apiCall: any): TestingAdapter => {
  const testingAdapter: TestingAdapter = async () => {
    try {
      await apiCall()
      return {
        isOk: true,
        message: null,
        payload: {
          success: 'success data',
        },
      }
    } catch (e) {
      return {
        isOk: false,
        message: "i'm a response in error.",
        payload: {
          error: 'failure data',
        },
      }
    }
  }

  return testingAdapter
}

describe('useAdapter', () => {
  it('should return loading payload then success payload', async () => {
    const successCall = vi
      .fn()
      .mockResolvedValue(new Promise(r => setTimeout(r, 200)))
    const { result } = renderHook(() =>
      useAdapter<SuccessPayload, FailurePayload>(getTestingAdapter(successCall))
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const expectedData = {
      success: 'success data',
    }

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(result.current.data).toEqual(expectedData)
    expect(result.current.error).toBeUndefined()
  })

  it('should return loading payload then failure payload', async () => {
    const failureCall = vi.fn().mockRejectedValue('Api error')
    const { result } = renderHook(() =>
      useAdapter<SuccessPayload, FailurePayload>(getTestingAdapter(failureCall))
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const expectedData = {
      error: 'failure data',
    }

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(result.current.error?.payload).toEqual(expectedData)
    expect(result.current.error?.message).toBe("i'm a response in error.")
  })
})
