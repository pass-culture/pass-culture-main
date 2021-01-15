import { DEFAULT_SEARCH_FILTERS } from 'components/pages/Offers/_constants'
import { client } from 'repository/pcapi/pcapiClient'

import {
  createStock,
  deleteStock,
  getURLErrors,
  loadFilteredOffers,
  updateOffersActiveStatus,
  updateStock,
} from '../pcapi'

jest.mock('repository/pcapi/pcapiClient', () => ({
  client: {
    delete: jest.fn(),
    get: jest.fn().mockResolvedValue({}),
    patch: jest.fn(),
    post: jest.fn(),
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
      const filters = {
        name: DEFAULT_SEARCH_FILTERS.name,
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
      }

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/offers?page=1')
    })

    it('should call offers route with filters when provided', async () => {
      // Given
      const filters = {
        name: 'OCS',
        venueId: 'AA',
        page: 2,
        status: 'expired',
        creationMode: 'manual',
      }

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith(
        '/offers?name=OCS&venueId=AA&status=expired&creationMode=manual&page=2'
      )
    })
  })

  describe('updateOffersActiveStatus', () => {
    describe('when updating all offers', () => {
      it('should call offers/all-active-status with proper params when filters are defaults', async () => {
        // given
        const body = {
          isActive: true,
        }

        // when
        await updateOffersActiveStatus(true, body)

        // then
        expect(client.patch).toHaveBeenCalledWith('/offers/all-active-status', {
          isActive: true,
          page: 1,
        })
      })

      it('should call offers/all-active-status with proper params when filters are set', async () => {
        // given
        const body = {
          isActive: true,
          offererId: 'IJ',
          venueId: 'KL',
          typeId: 'ThingType.AUDIOVISUEL',
          page: 2,
          status: 'expired',
          creationMode: 'imported',
        }

        // when
        await updateOffersActiveStatus(true, body)

        // then
        expect(client.patch).toHaveBeenCalledWith('/offers/all-active-status', {
          isActive: true,
          offererId: 'IJ',
          venueId: 'KL',
          typeId: 'ThingType.AUDIOVISUEL',
          page: 2,
          status: 'expired',
          creationMode: 'imported',
        })
      })
    })

    describe('when updating some offers', () => {
      it('should call offers/active-status with proper params', async () => {
        // given
        const body = {
          isActive: true,
          ids: ['A3', 'E9'],
        }

        // when
        await updateOffersActiveStatus(false, body)

        // then
        expect(client.patch).toHaveBeenCalledWith('/offers/active-status', {
          ids: ['A3', 'E9'],
          isActive: true,
        })
      })
    })
  })

  describe('deleteStock', () => {
    it('should delete stock given its id', () => {
      // When
      deleteStock('2E')

      // Then
      expect(client.delete).toHaveBeenCalledWith('/stocks/2E')
    })
  })

  describe('updateStock', () => {
    it('should update stock given its id and changes', () => {
      // When
      updateStock({
        beginningDatetime: '2020-12-26T23:00:00Z',
        bookingLimitDatetime: '2020-12-25T22:00:00Z',
        stockId: '2E',
        price: '14.01',
        quantity: '6',
      })

      // Then
      expect(client.patch).toHaveBeenCalledWith('/stocks/2E', {
        beginningDatetime: '2020-12-26T23:00:00Z',
        bookingLimitDatetime: '2020-12-25T22:00:00Z',
        price: '14.01',
        quantity: '6',
      })
    })
  })

  describe('createStock', () => {
    it('should create stock given its offerId and properties', () => {
      // when
      createStock({
        offerId: 'AE',
        beginningDatetime: '2020-12-24T23:00:00Z',
        bookingLimitDatetime: '2020-12-22T23:59:59Z',
        price: '15',
        quantity: '15',
      })

      // then
      expect(client.post).toHaveBeenCalledWith('/stocks', {
        offerId: 'AE',
        beginningDatetime: '2020-12-24T23:00:00Z',
        bookingLimitDatetime: '2020-12-22T23:59:59Z',
        price: '15',
        quantity: '15',
      })
    })
  })

  describe('getURLErrors', () => {
    it('should call the api correct POST route with url as a body param', () => {
      // given
      const url = 'http://ma-mauvaise-url'

      // when
      getURLErrors(url)

      // then
      expect(client.post).toHaveBeenCalledWith(`/offers/thumbnail-url-errors`, {
        url: url,
      })
    })
  })
})
