import '@testing-library/jest-dom'

import { renderHook } from '@testing-library/react-hooks'

import { useAdapter } from '..'

interface ISuccessPayload {
  success: string
}
interface IFailurePayload {
  error: string
}
type TTestingAdapter = Adapter<void, ISuccessPayload, IFailurePayload>

const getTestingAdapter = (apiCall: any): TTestingAdapter => {
  const testingAdapter: TTestingAdapter = async () => {
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
    const successCall = jest
      .fn()
      .mockResolvedValue(new Promise(r => setTimeout(r, 200)))
    const { result, waitForNextUpdate } = renderHook(() =>
      useAdapter<ISuccessPayload, IFailurePayload>(
        getTestingAdapter(successCall)
      )
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const expectedData = {
      success: 'success data',
    }
    await waitForNextUpdate()
    const updatedState = result.current
    expect(updatedState.data).toEqual(expectedData)
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.error).toBeUndefined()
  })

  it('should return loading payload then failure payload', async () => {
    const failureCall = jest.fn().mockRejectedValue('Api error')
    const { result, waitForNextUpdate } = renderHook(() =>
      useAdapter<ISuccessPayload, IFailurePayload>(
        getTestingAdapter(failureCall)
      )
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const expectedData = {
      error: 'failure data',
    }
    await waitForNextUpdate()
    const errorState = result.current
    expect(loadingState.data).toBeUndefined()
    expect(errorState.isLoading).toBe(false)
    expect(errorState.error?.payload).toEqual(expectedData)
    expect(errorState.error?.message).toBe("i'm a response in error.")
  })
})
