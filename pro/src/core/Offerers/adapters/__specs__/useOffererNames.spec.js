import '@testing-library/jest-dom'

import { apiV1 } from 'api/api'
import { renderHook } from '@testing-library/react-hooks'
import { useGetOffererNames } from '..'

describe('useOffererNames', () => {
  it('should return loading payload then success payload', async () => {
    const offererNames = [
      {
        id: 'AA',
        name: 'Structure AA',
      },
    ]

    jest
      .spyOn(apiV1, 'getOfferersListOfferersNames')
      .mockResolvedValue({ offerersNames: offererNames })

    const { result, waitForNextUpdate } = renderHook(() => useGetOffererNames())
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitForNextUpdate()
    expect(apiV1.getOfferersListOfferersNames).toHaveBeenCalled()

    const updatedState = result.current
    expect(updatedState.data).toEqual(offererNames)
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.error).toBeUndefined()
  })

  it('should return loading payload then error payload', async () => {
    jest
      .spyOn(apiV1, 'getOfferersListOfferersNames')
      .mockRejectedValue(new Error('Api error'))

    const { result, waitForNextUpdate } = renderHook(() => useGetOffererNames())
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitForNextUpdate()
    expect(apiV1.getOfferersListOfferersNames).toHaveBeenCalled()

    const updatedState = result.current
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.error.payload).toEqual([])
    expect(updatedState.error.message).toBe(
      'Nous avons rencontré un problème lors du chargemement des données'
    )
  })
})
