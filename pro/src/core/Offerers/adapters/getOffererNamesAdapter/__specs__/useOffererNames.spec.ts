import { waitFor, renderHook } from '@testing-library/react'

import { api } from 'apiClient/api'
import { GetOffererNameResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { useGetOffererNames } from '..'

describe('useOffererNames', () => {
  it('should return loading payload then success payload', async () => {
    const offererNames: GetOffererNameResponseModel[] = [
      {
        name: 'Structure AA',
        nonHumanizedId: 123,
      },
    ]

    jest
      .spyOn(api, 'listOfferersNames')
      .mockResolvedValue({ offerersNames: offererNames })

    const { result } = renderHook(() => useGetOffererNames({}))
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(api.listOfferersNames).toHaveBeenCalled()
    expect(result.current.data).toEqual(offererNames)
    expect(result.current.error).toBeUndefined()
  })

  it('should return loading payload then error payload', async () => {
    jest
      .spyOn(api, 'listOfferersNames')
      .mockRejectedValue(new Error('Api error'))

    const { result } = renderHook(() => useGetOffererNames({}))
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(api.listOfferersNames).toHaveBeenCalled()
    expect(result.current?.error?.payload).toEqual([])
    expect(result.current?.error?.message).toBe(GET_DATA_ERROR_MESSAGE)
  })
})
