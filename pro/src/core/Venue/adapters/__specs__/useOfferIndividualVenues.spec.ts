import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { renderHook } from '@testing-library/react-hooks'
import { useGetOfferIndividualVenues } from '..'

describe('useOffererNames', () => {
  it('should return loading payload then success payload', async () => {
    const apiVenue = {
      address: 'test address',
      audioDisabilityCompliant: false,
      bannerMeta: null,
      bannerUrl: null,
      bic: '',
      bookingEmail: '',
      businessUnitId: '',
      city: 'test city',
      comment: null,
      dateCreated: '2022-05-18T08:25:27.466460Z',
      dateModifiedAtLastProvider: '',
      departementCode: '61',
      description: 'test description',
      fieldsUpdated: [],
      iban: '',
      id: 'AAAA',
      isPermanent: true,
      isVirtual: false,
      lastProviderId: null,
      latitude: 48.87004,
      longitude: 2.3785,
      managingOffererId: 'AA',
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      nOffers: 0,
      name: 'Entreprise AA',
      postalCode: '75001',
      publicName: 'Entreprise AAAA public name',
      siret: '',
      thumbCount: 1,
      venueLabelId: null,
      venueTypeCode: 'OTHER',
      visualDisabilityCompliant: false,
      withdrawalDetails: null,
    }

    jest.spyOn(pcapi, 'getVenuesForOfferer').mockResolvedValue([apiVenue])

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
      },
    ]

    await waitForNextUpdate()
    expect(pcapi.getVenuesForOfferer).toHaveBeenCalled()
    const updatedState = result.current
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.data).toEqual(offerIndividualVenues)
    expect(updatedState.error).toBeUndefined()
  })

  it('should return loading payload then failure payload', async () => {
    jest
      .spyOn(pcapi, 'getVenuesForOfferer')
      .mockRejectedValue(new Error('Api error'))

    const { result, waitForNextUpdate } = renderHook(() =>
      useGetOfferIndividualVenues()
    )
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    await waitForNextUpdate()
    expect(pcapi.getVenuesForOfferer).toHaveBeenCalled()
    const errorState = result.current
    expect(loadingState.data).toBeUndefined()
    expect(errorState.isLoading).toBe(false)
    expect(errorState.error?.payload).toEqual([])
    expect(errorState.error?.message).toBe(GET_DATA_ERROR_MESSAGE)
  })
})
