import * as bookingsPreFilters from 'components/pages/Bookings/PreFilters/_constants'
import { DEFAULT_SEARCH_FILTERS } from 'components/pages/Offers/Offers/_constants'
import {
  getVenuesForOfferer,
  getVenueStats,
  loadFilteredBookingsRecap,
  signout,
  updateUserInformations,
} from 'repository/pcapi/pcapi'
import { client } from 'repository/pcapi/pcapiClient'
import { bookingRecapFactory } from 'utils/apiFactories'

import {
  deleteStock,
  loadFilteredOffers,
  postThumbnail,
  setHasSeenTutos,
  updateOffersActiveStatus,
  validateDistantImage,
} from '../pcapi'

jest.mock('repository/pcapi/pcapiClient', () => ({
  client: {
    delete: jest.fn(),
    get: jest.fn().mockResolvedValue({}),
    patch: jest.fn(),
    post: jest.fn(),
    postWithFormData: jest.fn(),
  },
}))

describe('pcapi', () => {
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

  describe('getVenueStats', () => {
    it('should get stats for given venue', () => {
      // When
      getVenueStats('3F')

      // Then
      expect(client.get).toHaveBeenCalledWith('/venues/3F/stats')
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

  describe('signout', () => {
    it('should sign out the user', () => {
      // When
      signout()

      // Then
      expect(client.get).toHaveBeenCalledWith('/users/signout')
    })
  })

  describe('validateDistantImage', () => {
    it('should call the api correct POST route with url as a body param', () => {
      // given
      const url = 'http://ma-mauvaise-url'

      // when
      validateDistantImage(url)

      // then
      expect(client.post).toHaveBeenCalledWith(`/offers/thumbnail-url-validation`, {
        url: url,
      })
    })
  })

  describe('postThumbnail', () => {
    it('should call the api correct POST route with thumbnail info as body param', () => {
      // given
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('offererId', 'BB')
      body.append('credit', 'Mon crédit')
      body.append('croppingRectX', '12')
      body.append('croppingRectY', '32')
      body.append('croppingRectHeight', '350')
      body.append('thumb', file)
      body.append('thumbUrl', '')

      // when
      postThumbnail('BB', 'AA', 'Mon crédit', file, '', '12', '32', '350')

      // then
      expect(client.postWithFormData).toHaveBeenCalledWith(`/offers/thumbnails`, body)
    })
  })

  describe('hasSeenTutos', () => {
    it('should call api', () => {
      // when
      setHasSeenTutos()

      // then
      expect(client.patch).toHaveBeenCalledWith('/users/tuto-seen')
    })
  })

  describe('update profile informations', () => {
    it('should call api patch with user informations', () => {
      // when
      const body = {
        firstName: 'Example',
        lastName: 'User',
        email: 'example.user@example.com',
        phoneNumber: '0606060606',
      }

      updateUserInformations(body)

      // then
      expect(client.patch).toHaveBeenCalledWith('/users/current', body)
    })
  })

  describe('getVenuesForOfferer', () => {
    beforeEach(() => {
      const returnedResponse = {
        venues: [
          {
            id: 'AE',
            name: 'Librairie Kléber',
            isVirtual: false,
          },
        ],
      }
      client.get.mockResolvedValue(returnedResponse)
    })

    it('should return venues value', async () => {
      // When
      const venues = await getVenuesForOfferer()

      // Then
      expect(venues).toHaveLength(1)
      expect(venues[0]).toStrictEqual({
        id: 'AE',
        name: 'Librairie Kléber',
        isVirtual: false,
      })
    })

    it('should call api with offererId in query params when given', async () => {
      // When
      await getVenuesForOfferer({ offererId: 'A4' })

      // Then
      expect(client.get).toHaveBeenCalledWith('/venues?offererId=A4')
    })

    it('should call api with validadedForUser as true when no offererId was given', async () => {
      // When
      await getVenuesForOfferer()

      // Then
      expect(client.get).toHaveBeenCalledWith('/venues?validatedForUser=true')
    })
  })

  describe('loadFilteredBookingsRecap', () => {
    const returnedResponse = {
      page: 1,
      pages: 1,
      total: 1,
      bookings_recap: [bookingRecapFactory()],
    }

    beforeEach(() => {
      client.get.mockResolvedValue(returnedResponse)
    })

    it('should return api response', async () => {
      // When
      const response = await loadFilteredBookingsRecap({})

      // Then
      expect(response).toBe(returnedResponse)
    })

    it('should call offers route with "page=1" when no other filters are provided', async () => {
      // Given
      const filters = {
        page: 1,
      }

      // When
      await loadFilteredBookingsRecap(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/bookings/pro?page=1')
    })

    it('should call offers route with "page=1" when provided filters are defaults', async () => {
      // Given
      const filters = {
        page: 1,
        venueId: bookingsPreFilters.ALL_VENUES,
      }

      // When
      await loadFilteredBookingsRecap(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/bookings/pro?page=1')
    })

    it('should call offers route with filters when provided', async () => {
      // Given
      const filters = {
        venueId: 'AA',
        page: 2,
      }

      // When
      await loadFilteredBookingsRecap(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/bookings/pro?page=2&venueId=AA')
    })
  })
})
