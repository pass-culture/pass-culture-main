import { getFilteredBookingsCSV, postThumbnail } from 'repository/pcapi/pcapi'
import { client } from 'repository/pcapi/pcapiClient'

vi.mock('repository/pcapi/pcapiClient', () => ({
  client: {
    delete: vi.fn(),
    get: vi.fn().mockResolvedValue({}),
    getPlainText: vi.fn().mockResolvedValue(''),
    patch: vi.fn(),
    post: vi.fn().mockResolvedValue({}),
    postWithFormData: vi.fn(),
  },
}))

vi.mock('utils/date', async () => {
  const actual = (await vi.importActual('utils/date')) || {}
  return {
    ...actual,
    getToday: vi.fn(() => new Date(2020, 8, 12)),
  }
})

describe('pcapi', () => {
  describe('postThumbnail', () => {
    it('should call the api correct POST route with thumbnail info as body param', () => {
      // given
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('thumb', file)
      body.append('credit', 'Mon crédit')
      body.append('croppingRectX', '12')
      body.append('croppingRectY', '32')
      body.append('croppingRectHeight', '350')
      body.append('croppingRectWidth', '220')
      body.append('thumbUrl', '')

      // when
      postThumbnail('AA', file, 'Mon crédit', '', 12, 32, 350, 220)

      // then
      expect(client.postWithFormData).toHaveBeenCalledWith(
        `/offers/thumbnails`,
        body
      )
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
        eventDate: '2020-09-13',
        page: 2,
        bookingPeriodBeginningDate: '2020-07-08',
        bookingPeriodEndingDate: '2020-09-04',
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
})
