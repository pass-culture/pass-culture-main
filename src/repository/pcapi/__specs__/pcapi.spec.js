import { client } from 'repository/pcapi/pcapiClient'

import { ALL_OFFERS, ALL_VENUES } from '../../../components/pages/Offers/_constants'
import { loadFilteredOffers } from '../pcapi'

jest.mock('repository/pcapi/pcapiClient', () => ({
  client: {
    get: jest.fn().mockResolvedValue({}),
  },
}))

describe('pcapi', () => {
  afterEach(() => {
    client.get.mockReset()
  })

  describe('loadFilteredOffers', () => {
    const returnedResponse = {
      offers: [
        {
          hasBookingLimitDatetimesPassed: false,
          id: 'AAA',
          isActive: false,
          isEditable: true,
          isEvent: true,
          isThing: false,
          name: 'Drunk - VF',
          stocks: [],
          thumbUrl: '',
          type: 'EventType.CINEMA',
          venue: {
            id: 'BBB',
            isVirtual: false,
            managingOffererId: 'CCC',
            name: 'Mon petit cinéma',
            offererName: 'Mon groupe de cinémas',
          },
          venueId: 'AAA',
        },
      ],
      page: 1,
      page_count: 1,
      total_count: 1,
    }

    beforeEach(() => {
      client.get.mockResolvedValue(returnedResponse)
    })

    it('should return api response', async () => {
      // When
      const response = await loadFilteredOffers({})

      // Then
      expect(response).toBe(returnedResponse)
    })

    it('should call offers route with "page=1" query param by default', async () => {
      // Given
      const filters = {}

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/offers?page=1')
    })

    it('should call offers route with "page=1" when provided filters are defaults', async () => {
      // Given
      const filters = { nameSearchValue: ALL_OFFERS, selectedVenueId: ALL_VENUES }

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/offers?page=1')
    })

    it('should call offers route with filters when provided', async () => {
      // Given
      const statusFilters = { active: false, inactive: false }
      const filters = { nameSearchValue: 'OCS', selectedVenueId: 'AA', page: 2, statusFilters }

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith(
        '/offers?name=OCS&venueId=AA&page=2&active=false&inactive=false'
      )
    })

    it('should call offers route without status filters when none are provided', async () => {
      // Given
      const filters = { statusFilters: {} }

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/offers?page=1')
    })
  })
})
