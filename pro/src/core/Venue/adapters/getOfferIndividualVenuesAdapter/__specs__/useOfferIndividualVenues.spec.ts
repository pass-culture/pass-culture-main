import { renderHook, waitFor } from '@testing-library/react'

import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ApiError } from 'apiClient/v2'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { dehumanizeId } from 'utils/dehumanize'

import getOfferIndividualVenuesAdapter from '../getOfferIndividualVenuesAdapter'
import useGetOfferIndividualVenues from '../useOfferIndividualVenues'

describe('useGetOfferIndividualVenues', () => {
  it("should not call api when no offererId isn't provided or admin users", async () => {
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })

    const { result } = renderHook(() =>
      useGetOfferIndividualVenues({ isAdmin: true })
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(api.getVenues).not.toHaveBeenCalled()
    expect(result.current.data).toEqual([])
    expect(result.current.error).toBeUndefined()
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
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: false,
      }
      offerIndividualVenues = [
        {
          id: 'AAAA',
          nonHumanizedId: 1,
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
          hasMissingReimbursementPoint: false,
          hasCreatedOffer: true,
        },
      ]
      jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [apiVenue] })
    })

    it('should call api for all venues', async () => {
      const { result } = renderHook(() =>
        useGetOfferIndividualVenues({ isAdmin: false })
      )
      const loadingState = result.current

      expect(loadingState.data).toBeUndefined()
      expect(loadingState.isLoading).toBe(true)
      expect(loadingState.error).toBeUndefined()

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
      expect(api.getVenues).toHaveBeenCalledWith(null, true, undefined)
      expect(result.current.data).toEqual(offerIndividualVenues)
      expect(result.current.error).toBeUndefined()
    })

    it('should call api for venues of given offerer', async () => {
      const { result } = renderHook(() =>
        useGetOfferIndividualVenues({ isAdmin: false, offererId: 'AK' })
      )
      const loadingState = result.current

      expect(loadingState.data).toBeUndefined()
      expect(loadingState.isLoading).toBe(true)
      expect(loadingState.error).toBeUndefined()

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
      expect(api.getVenues).toHaveBeenCalledWith(null, true, dehumanizeId('AK'))
      expect(result.current.data).toEqual(offerIndividualVenues)
      expect(result.current.error).toBeUndefined()
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

    const { result } = renderHook(() =>
      useGetOfferIndividualVenues({ isAdmin: false })
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(api.getVenues).toHaveBeenCalled()
    expect(result.current.error?.payload).toEqual([])
    expect(result.current.error?.message).toBe(GET_DATA_ERROR_MESSAGE)
  })
})
