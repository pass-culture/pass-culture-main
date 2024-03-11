import { waitFor, renderHook } from '@testing-library/react'

import { api } from 'apiClient/api'
import { GetOffererNameResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { getOffererNameFactory } from 'utils/individualApiFactories'

import { useGetOffererNames } from '..'

describe('useOffererNames', () => {
  it('should return loading payload then success payload', async () => {
    const offererNames: GetOffererNameResponseModel[] = [
      getOffererNameFactory({
        name: 'Structure AA',
        id: 123,
      }),
    ]

    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: offererNames,
    })

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
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue(new Error('Api error'))

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
