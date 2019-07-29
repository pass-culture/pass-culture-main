import { mapStateToProps } from '../BookingsContainer'
import { API_URL } from '../../../../utils/config'

describe('src | components | pages | Bookings | BookingsContainer', () => {
  describe('mapStateToProps', () => {
    describe('pathToCsvFile', () => {
      it("should build the csv path without any filters when venueId is 'all'", () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: 'all',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile: API_URL + '/bookings/csv',
          showButtons: true,
          showOfferSection: false,
        })
      })

      it('should build the csv path including only digital venues for a specific offerId and period when isFilteredByDigitalVenues is true, offerId, dateFrom and dateTo are provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '2019-07-17T14:35:31.702139Z',
            bookingsTo: '2019-07-17T14:35:31.702139Z',
            isFilteredByDigitalVenues: true,
            offerId: 'AR',
            venueId: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile:
            API_URL +
            '/bookings/csv?onlyDigitalVenues=true&offerId=AR&dateFrom=2019-07-17T14:35:31.702139Z&dateTo=2019-07-17T14:35:31.702139Z',
          showButtons: true,
          showOfferSection: true,
        })
      })

      it('should build the csv path including all offers for a specific venue when offerId is `all and venueId is provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: 'all',
            venueId: 'F51',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile: API_URL + '/bookings/csv?venueId=F51',
          showButtons: true,
          showOfferSection: true,
        })
      })

      it('should build the csv path using venueId, offerId, dateFrom and dateTo as filters when provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: new Date('2019-07-17T14:35:31.000Z').toISOString(),
            bookingsTo: new Date('2019-07-17T14:35:31.000Z').toISOString(),
            isFilteredByDigitalVenues: false,
            offerId: 'CY',
            venueId: 'F51',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile:
            API_URL +
            '/bookings/csv?venueId=F51&offerId=CY&dateFrom=2019-07-17T14:35:31.000Z&dateTo=2019-07-17T14:35:31.000Z',
          showButtons: true,
          showOfferSection: true,
        })
      })
    })

    describe('showButtons', () => {
      it('should be true when isFilteredByDigitalVenues is true, offerId, bookingsFrom and bookingsTo are provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '2019-07-28T21:59:00Z',
            bookingsTo: '2019-07-28T21:59:00Z',
            isFilteredByDigitalVenues: true,
            offerId: 'A4',
            venueId: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showButtons', true)
      })

      it('should be true when a venueId, offerId, bookingsFrom and bookingsTo are provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '2019-07-28T21:59:00Z',
            bookingsTo: '2019-07-28T21:59:00Z',
            isFilteredByDigitalVenues: false,
            offerId: 'CY',
            venueId: 'G2YU',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showButtons', true)
      })

      it('should be false when venueId is provided but offerId is not provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: 'CY',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showButtons', false)
      })

      it('should be false when venueId and offerId are provided, but not bookingsFrom and bookingsTo', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: 'A4',
            venueId: 'CY',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showButtons', false)
      })

      it('should be true when venueId is `all`', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: 'all',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showButtons', true)
      })

      it('should be true when offerId is `all`', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: 'all',
            venueId: 'CY',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showButtons', true)
      })
    })

    describe('showOfferSection', () => {
      it('should be false when isFilteredByDigitalVenues is false and no venueId is provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', false)
      })

      it('should be true when a venueId is provided', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: 'CY',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', true)
      })

      it('should be true when isFilteredByDigitalVenues is true', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: true,
            offerId: '',
            venueId: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', true)
      })

      it('should be false when venueId is `all`', () => {
        // given
        const state = {
          bookingSummary: {
            bookingsFrom: '',
            bookingsTo: '',
            isFilteredByDigitalVenues: true,
            offerId: '',
            venueId: 'all',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', false)
      })
    })
  })
})
