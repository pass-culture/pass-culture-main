import { renderHook, waitFor } from '@testing-library/react'

import { api } from 'apiClient/api'
import { GetIndividualOfferFactory } from 'utils/apiFactories'

import { useGetOfferIndividual } from '..'

describe('useGetOfferIndividual', () => {
  it('should return loading payload then success payload', async () => {
    jest.spyOn(api, 'getOffer').mockResolvedValue(GetIndividualOfferFactory())

    const { result } = renderHook(() => useGetOfferIndividual('YA'))
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const offerIndividual = {
      accessibility: {
        audio: false,
        mental: false,
        motor: false,
        none: true,
        visual: false,
      },
      author: '',
      bookingEmail: '',
      description: '',
      durationMinutes: null,
      ean: '',
      externalTicketOfficeUrl: '',
      id: 'OFFER1',
      image: undefined,
      isActive: true,
      isDigital: false,
      isDuo: true,
      isEducational: false,
      isEvent: false,
      isNational: true,
      isbn: '',
      lastProvider: null,
      lastProviderName: null,
      musicSubType: '',
      musicType: '',
      name: 'Le nom de l’offre 1',
      nonHumanizedId: 1,
      offererId: 'OFFERER1',
      offererName: 'La nom de la structure 1',
      performer: '',
      priceCategories: undefined,
      showSubType: '',
      showType: '',
      speaker: '',
      stageDirector: '',
      status: 'ACTIVE',
      stocks: [
        {
          activationCodes: [],
          activationCodesExpirationDatetime: null,
          beginningDatetime: null,
          bookingLimitDatetime: null,
          bookingsQuantity: 0,
          dateCreated: new Date('2020-04-12T19:31:12.000Z'),
          hasActivationCode: false,
          id: 'STOCK1',
          isEventDeletable: true,
          isEventExpired: false,
          isSoftDeleted: false,
          nonHumanizedId: 1,
          offerId: 'OFFER1',
          price: 10,
          quantity: null,
          remainingQuantity: 2,
        },
      ],
      subcategoryId: 'SEANCE_CINE',
      url: '',
      venue: {
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: true,
          visual: false,
        },
        address: 'Ma Rue',
        city: 'Ma Ville',
        departmentCode: '973',
        id: 'VENUE1',
        isVirtual: false,
        name: 'Le nom du lieu 1',
        offerer: {
          id: 'OFFERER1',
          name: 'La nom de la structure 1',
          nonHumanizedId: 3,
        },
        postalCode: '11100',
        publicName: 'Mon Lieu',
      },
      venueId: 'AA',
      visa: '',
      withdrawalDelay: null,
      withdrawalDetails: '',
      withdrawalType: null,
    }

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(api.getOffer).toHaveBeenCalled()
    expect(result.current.data).toEqual(offerIndividual)
    expect(result.current.error).toBeUndefined()
  })
})
