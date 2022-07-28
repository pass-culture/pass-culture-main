import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { ALL_OFFERERS, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import {
  generateOffererApiKey,
  getFilteredBookingsCSV,
  getVenueStats,
  getVenuesForOfferer,
  invalidateBooking,
  loadFilteredBookingsRecap,
  signout,
  updateUserInformations,
  validateBooking,
  buildGetOfferersQuery,
  deleteStock,
  loadFilteredOffers,
  postThumbnail,
  setHasSeenTutos,
  updateAllOffersActiveStatus,
  updateOffersActiveStatus,
  validateDistantImage,
} from 'repository/pcapi/pcapi'
import { client } from 'repository/pcapi/pcapiClient'
import { bookingRecapFactory } from 'utils/apiFactories'

jest.mock('repository/pcapi/pcapiClient', () => ({
  client: {
    delete: jest.fn(),
    get: jest.fn().mockResolvedValue({}),
    getPlainText: jest.fn().mockResolvedValue(''),
    patch: jest.fn(),
    post: jest.fn().mockResolvedValue({}),
    postWithFormData: jest.fn(),
  },
}))

jest.mock('utils/date', () => {
  return {
    ...jest.requireActual('utils/date'),
    getToday: jest.fn().mockReturnValue(new Date(2020, 8, 12)),
  }
})

describe('pcapi', () => {
  describe('loadFilteredOffers', () => {
    const returnedResponse = [
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
    ]

    beforeEach(() => {
      // @ts-expect-error ts-migrate(2339) FIXME: Property 'mockResolvedValue' does not exist on typ... Remove this comment to see the full error message
      client.get.mockResolvedValue(returnedResponse)
    })

    it('should return api response', async () => {
      // When
      const response = await loadFilteredOffers({})

      // Then
      expect(response).toBe(returnedResponse)
    })

    it('should call offers route without query params when provided filters are defaults', async () => {
      // Given
      const filters = {
        // @ts-expect-error ts-migrate(2339) FIXME: Property 'name' does not exist on type 'TSearchFil... Remove this comment to see the full error message
        name: DEFAULT_SEARCH_FILTERS.name,
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
      }

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith('/offers')
    })

    it('should call offers route with filters when provided', async () => {
      // Given
      const filters = {
        nameOrIsbn: 'OCS',
        venueId: 'AA',
        status: 'expired',
        creationMode: 'manual',
      }

      // When
      await loadFilteredOffers(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith(
        '/offers?nameOrIsbn=OCS&venueId=AA&status=expired&creationMode=manual'
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
        await updateAllOffersActiveStatus(body)

        // then
        expect(client.patch).toHaveBeenCalledWith('/offers/all-active-status', {
          isActive: true,
        })
      })

      it('should call offers/all-active-status with proper params when filters are set', async () => {
        // given
        const body = {
          isActive: true,
          offererId: 'IJ',
          venueId: 'KL',
          categoryId: 'CINEMA',
          status: 'expired',
          creationMode: 'imported',
        }

        // when
        // @ts-expect-error Impossible d'assigner le type 'string' au type 'number'
        await updateAllOffersActiveStatus(body)

        // then
        expect(client.patch).toHaveBeenCalledWith('/offers/all-active-status', {
          isActive: true,
          offererId: 'IJ',
          venueId: 'KL',
          categoryId: 'CINEMA',
          status: 'expired',
          creationMode: 'imported',
        })
      })
    })

    describe('when updating some offers', () => {
      it('should call offers/active-status with proper params', async () => {
        // when
        await updateOffersActiveStatus(['A3', 'E9'], true)

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

  describe('generateOffererApiKey', () => {
    it('should post an api key', async () => {
      // When
      await generateOffererApiKey('3F')

      // Then
      expect(client.post).toHaveBeenCalledWith('/offerers/3F/api_keys', {})
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
      expect(client.post).toHaveBeenCalledWith(
        `/offers/thumbnail-url-validation`,
        {
          url: url,
        }
      )
    })
  })

  describe('postThumbnail', () => {
    it('should call the api correct POST route with thumbnail info as body param', () => {
      // given
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('credit', 'Mon crédit')
      body.append('croppingRectX', '12')
      body.append('croppingRectY', '32')
      body.append('croppingRectHeight', '350')
      body.append('croppingRectWidth', '220')
      body.append('thumb', file)
      body.append('thumbUrl', '')

      // when
      postThumbnail('AA', 'Mon crédit', file, '', '12', '32', '350', '220')

      // then
      expect(client.postWithFormData).toHaveBeenCalledWith(
        `/offers/thumbnails`,
        body
      )
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
      // @ts-expect-error ts-migrate(2339) FIXME: Property 'mockResolvedValue' does not exist on typ... Remove this comment to see the full error message
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
      // @ts-expect-error ts-migrate(2322) FIXME: Type 'string' is not assignable to type 'null | un... Remove this comment to see the full error message
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

    it('should not add offererId in query params when offererId value is ALL_OFFERERS', async () => {
      // When
      // @ts-expect-error ts-migrate(2322) FIXME: Type 'string' is not assignable to type 'null | un... Remove this comment to see the full error message
      await getVenuesForOfferer({ offererId: ALL_OFFERERS })

      // Then
      expect(client.get).toHaveBeenCalledWith('/venues')
    })
  })

  describe('getFilteredBookingsCSV', () => {
    const returnedResponse = "i'm a text response"

    beforeEach(() => {
      // @ts-expect-error ts-migrate(2339) FIXME: Property 'mockResolvedValue' does not exist on typ... Remove this comment to see the full error message
      client.getPlainText.mockResolvedValue(returnedResponse)
    })

    it('should return api response', async () => {
      // When
      const response = await getFilteredBookingsCSV({})

      // Then
      expect(response).toBe(returnedResponse)
    })

    it('should call bookings csv route with "page=1" and default period when no other filters are provided', async () => {
      // Given
      const filters = {
        page: 1,
      }

      // When
      await getFilteredBookingsCSV(filters)

      // Then
      expect(client.getPlainText).toHaveBeenCalledWith(
        '/bookings/csv?page=1&bookingPeriodBeginningDate=2020-08-13&bookingPeriodEndingDate=2020-09-12&bookingStatusFilter=booked'
      )
    })

    it('should call offers route with filters when provided', async () => {
      // Given
      const filters = {
        venueId: 'AA',
        eventDate: new Date(2020, 8, 13),
        page: 2,
        bookingPeriodBeginningDate: new Date(2020, 6, 8),
        bookingPeriodEndingDate: new Date(2020, 8, 4),
        bookingStatusFilter: 'validated',
      }

      // When
      await getFilteredBookingsCSV(filters)

      // Then
      expect(client.getPlainText).toHaveBeenCalledWith(
        '/bookings/csv?page=2&venueId=AA&eventDate=2020-09-13&bookingPeriodBeginningDate=2020-07-08&bookingPeriodEndingDate=2020-09-04&bookingStatusFilter=validated'
      )
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
      // @ts-expect-error ts-migrate(2339) FIXME: Property 'mockResolvedValue' does not exist on typ... Remove this comment to see the full error message
      client.get.mockResolvedValue(returnedResponse)
    })

    it('should return api response', async () => {
      // When
      const response = await loadFilteredBookingsRecap({})

      // Then
      expect(response).toBe(returnedResponse)
    })

    it('should call offers route with "page=1" and default period when no other filters are provided', async () => {
      // Given
      const filters = {
        page: 1,
      }

      // When
      await loadFilteredBookingsRecap(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith(
        '/bookings/pro?page=1&bookingPeriodBeginningDate=2020-08-13&bookingPeriodEndingDate=2020-09-12&bookingStatusFilter=booked'
      )
    })

    it('should call offers route with "page=1" and default period when provided filters are defaults', async () => {
      // Given
      const filters = {
        page: 1,
        venueId: DEFAULT_PRE_FILTERS.offerVenueId,
        eventDate: DEFAULT_PRE_FILTERS.offerEventDate,
      }

      // When
      await loadFilteredBookingsRecap(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith(
        '/bookings/pro?page=1&bookingPeriodBeginningDate=2020-08-13&bookingPeriodEndingDate=2020-09-12&bookingStatusFilter=booked'
      )
    })

    it('should call offers route with filters when provided', async () => {
      // Given
      const filters = {
        venueId: 'AA',
        eventDate: new Date(2020, 8, 13),
        page: 2,
        bookingPeriodBeginningDate: new Date(2020, 6, 8),
        bookingPeriodEndingDate: new Date(2020, 8, 4),
        bookingStatusFilter: 'validated',
      }

      // When
      await loadFilteredBookingsRecap(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith(
        '/bookings/pro?page=2&venueId=AA&eventDate=2020-09-13&bookingPeriodBeginningDate=2020-07-08&bookingPeriodEndingDate=2020-09-04&bookingStatusFilter=validated'
      )
    })

    it('should call bookings route with default period filter when not provided', async () => {
      // Given
      const filters = {
        venueId: 'AA',
        eventDate: new Date(2020, 8, 13),
        page: 2,
      }

      // When
      await loadFilteredBookingsRecap(filters)

      // Then
      expect(client.get).toHaveBeenCalledWith(
        '/bookings/pro?page=2&venueId=AA&eventDate=2020-09-13&bookingPeriodBeginningDate=2020-08-13&bookingPeriodEndingDate=2020-09-12&bookingStatusFilter=booked'
      )
    })
  })

  describe('validateBooking', () => {
    it('should patch booking with it code', async () => {
      // When
      validateBooking('A5DS6Q')

      // Then
      expect(client.patch).toHaveBeenCalledWith('/v2/bookings/use/token/A5DS6Q')
    })
  })

  describe('invalidateBooking', () => {
    it('should patch booking with it code', async () => {
      // When
      invalidateBooking('A5DS6Q')

      // Then
      expect(client.patch).toHaveBeenCalledWith(
        '/v2/bookings/keep/token/A5DS6Q'
      )
    })
  })

  describe('buildGetOfferersQuery', () => {
    describe('when there is one keyword', () => {
      it('should create api url with keywords params only', () => {
        // given
        const keywords = ['example']
        const page = '7'
        const filters = { keywords, page }

        // when
        // @ts-expect-error ts-migrate(2345) FIXME: Argument of type '{ keywords: string[]; page: stri... Remove this comment to see the full error message
        const result = buildGetOfferersQuery(filters)

        // then
        expect(result).toBe('?keywords=example&page=7')
      })
    })

    describe('when there is multiple keywords', () => {
      it('should create api url with keywords params', () => {
        // given
        const keywords = ['example', 'keyword']
        const page = '666'
        const filters = { keywords, page }

        // when
        // @ts-expect-error ts-migrate(2345) FIXME: Argument of type '{ keywords: string[]; page: stri... Remove this comment to see the full error message
        const result = buildGetOfferersQuery(filters)

        // then
        expect(result).toBe('?keywords=example+keyword&page=666')
      })
    })
  })
})
