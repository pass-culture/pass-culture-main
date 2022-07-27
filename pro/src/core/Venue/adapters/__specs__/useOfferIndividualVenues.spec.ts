import '@testing-library/jest-dom'

import { renderHook } from '@testing-library/react-hooks'

import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { useGetOfferIndividualVenues } from '..'

describe('useOffererNames', () => {
  it('should return loading payload then success payload', async () => {
    const apiVenue: VenueListItemResponseModel = {
      audioDisabilityCompliant: false,
      bookingEmail: '',
      businessUnit: null,
      businessUnitId: null,
      id: 'AAAA',
      isVirtual: false,
      managingOffererId: 'AA',
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      name: 'Entreprise AA',
      offererName: 'Structure AA',
      publicName: 'Entreprise AAAA public name',
      siret: '',
      visualDisabilityCompliant: false,
      withdrawalDetails: null,
    }

    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [apiVenue] })

    const { result, waitForNextUpdate } = renderHook(() =>
      useGetOfferIndividualVenues()
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const offerIndividualVenues = [
      {
        id: apiVenue.id,
        isVirtual: apiVenue.isVirtual,
        managingOffererId: apiVenue.managingOffererId,
        name: apiVenue.publicName,
        withdrawalDetails: apiVenue.withdrawalDetails,
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          visual: false,
          none: true,
        },
      },
    ]

    await waitForNextUpdate()
    expect(api.getVenues).toHaveBeenCalled()
    const updatedState = result.current
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.data).toEqual(offerIndividualVenues)
    expect(updatedState.error).toBeUndefined()
  })

  it('should return loading payload then failure payload', async () => {
    jest.spyOn(api, 'getVenues').mockRejectedValue(new Error('Api error'))

    const { result, waitForNextUpdate } = renderHook(() =>
      useGetOfferIndividualVenues()
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
