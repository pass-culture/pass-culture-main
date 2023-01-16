import '@testing-library/jest-dom'

import { renderHook } from '@testing-library/react-hooks'

import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ApiError } from 'apiClient/v2'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'

import getOfferIndividualVenuesAdapter from '../getOfferIndividualVenuesAdapter'
import useGetOfferIndividualVenues from '../useOfferIndividualVenues'

describe('useGetOfferIndividualVenues', () => {
  it("should not call api when no offererId isn't provided or admin users", async () => {
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })

    const { result, waitForNextUpdate } = renderHook(() =>
      useGetOfferIndividualVenues({ isAdmin: true })
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitForNextUpdate()
    expect(api.getVenues).not.toHaveBeenCalled()
    const updatedState = result.current
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.data).toEqual([])
    expect(updatedState.error).toBeUndefined()
  })

  describe('should return loading payload then success payload', () => {
    let apiVenue: VenueListItemResponseModel
    let offerIndividualVenues: TOfferIndividualVenue[]
    beforeEach(() => {
      apiVenue = {
        audioDisabilityCompliant: false,
        bookingEmail: '',
        nonHumanizedId: 1,
        id: 'AAAA',
        isVirtual: false,
        managingOffererId: 'AA',
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        name: 'Entreprise AA',
        offererName: 'Structure AA',
        siret: '',
        visualDisabilityCompliant: false,
        withdrawalDetails: null,
      }
      offerIndividualVenues = [
        {
          id: 'AAAA',
          isVirtual: false,
          managingOffererId: 'AA',
          name: 'Entreprise AA',
          withdrawalDetails: null,
          accessibility: {
            audio: false,
            mental: false,
            motor: false,
            visual: false,
            none: true,
          },
        },
      ]
      jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [apiVenue] })
    })

    it('should call api for all venues', async () => {
      const { result, waitForNextUpdate } = renderHook(() =>
        useGetOfferIndividualVenues({ isAdmin: false })
      )
      const loadingState = result.current

      expect(loadingState.data).toBeUndefined()
      expect(loadingState.isLoading).toBe(true)
      expect(loadingState.error).toBeUndefined()

      await waitForNextUpdate()
      expect(api.getVenues).toHaveBeenCalledWith(null, null, true, undefined)
      const updatedState = result.current
      expect(updatedState.isLoading).toBe(false)
      expect(updatedState.data).toEqual(offerIndividualVenues)
      expect(updatedState.error).toBeUndefined()
    })

    it('should call api for venues of given offerer', async () => {
      const { result, waitForNextUpdate } = renderHook(() =>
        useGetOfferIndividualVenues({ isAdmin: false, offererId: 'AA' })
      )
      const loadingState = result.current

      expect(loadingState.data).toBeUndefined()
      expect(loadingState.isLoading).toBe(true)
      expect(loadingState.error).toBeUndefined()

      await waitForNextUpdate()
      expect(api.getVenues).toHaveBeenCalledWith(null, null, true, 'AA')
      const updatedState = result.current
      expect(updatedState.isLoading).toBe(false)
      expect(updatedState.data).toEqual(offerIndividualVenues)
      expect(updatedState.error).toBeUndefined()
    })
  })

  it('should call api and get error', async () => {
    jest
      .spyOn(api, 'getVenues')
      .mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, {} as ApiResult, '')
      )

    expect(await getOfferIndividualVenuesAdapter({})).toStrictEqual({
      isOk: false,
      message: GET_DATA_ERROR_MESSAGE,
      payload: [],
    })
  })

  it('should return loading payload then failure payload', async () => {
    jest.spyOn(api, 'getVenues').mockRejectedValue(new Error('Api error'))

    const { result, waitForNextUpdate } = renderHook(() =>
      useGetOfferIndividualVenues({ isAdmin: false })
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitForNextUpdate()
    expect(api.getVenues).toHaveBeenCalled()
    const errorState = result.current
    expect(loadingState.data).toBeUndefined()
    expect(errorState.isLoading).toBe(false)
    expect(errorState.error?.payload).toEqual([])
    expect(errorState.error?.message).toBe(GET_DATA_ERROR_MESSAGE)
  })
})
