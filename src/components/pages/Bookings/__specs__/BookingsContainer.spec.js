import { mapStateToProps } from '../BookingsContainer'

describe('src | components | pages | Bookings | BookingsContainer', () => {
  describe('mapStateToProps', () => {
    describe('pathToCsvFile', () => {
      describe('when a venue is selected', () => {
        it('should limit csv to this venue', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: false,
              selectedVenue: 'F51',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv?venueId=F51',
            showButtons: true,
          })
        })

        it("should target the API without filter on venueId when the 'all' option selected", () => {
          // given
          const state = {
            bookingSummary: {
              selectedVenue: 'all',
              isFilterByDigitalVenues: false,
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv',
            showButtons: true,
          })
        })
      })

      describe('when filtering on digital venue', () => {
        it('should limit csv to these digital venues', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: true,
              selectedVenue: '',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv?onlyDigitalVenues=true',
            showButtons: true,
          })
        })
      })

      describe('showButtons', () => {
        it('should be displayed when downloading digital venues', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: true,
              selectedVenue: '',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv?onlyDigitalVenues=true',
            showButtons: true,
          })
        })

        it('should be displayed when a venue is selected', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: false,
              selectedVenue: 'G2YU',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv?venueId=G2YU',
            showButtons: true,
          })
        })

        it('should be displayed when the `all venues` option is selected', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: false,
              selectedVenue: 'all',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv',
            showButtons: true,
          })
        })
      })
    })
  })
})
