import { mapStateToProps } from '../BookingsContainer'

describe('src | components | pages | Bookings | BookingsContainer', () => {
  describe('mapStateToProps', () => {
    describe('pathToCsvFile', () => {
      describe('when no filters', () => {
        it('should target the API without filter', () => {
          // given
          const state = {}

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toHaveProperty('pathToCsvFile', 'http://localhost/bookings/csv')
        })
      });

      describe('when a venue is selected', () => {
        it('should limit csv to this venue', () => {
          // given
          const state = {
            bookingSummary: {
              selectedVenue: 'F51'
            }
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toHaveProperty('pathToCsvFile', 'http://localhost/bookings/csv?venueId=F51')
        })

        it('should venueId should be empty when the \'all\' option selected', () => {
          // given
          const state = {
            bookingSummary: {
              selectedVenue: 'all'
            }
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toHaveProperty('pathToCsvFile', 'http://localhost/bookings/csv')
        })
      });

      describe('when filtering on digital venue', () => {
        it('should limit csv to these digital venues', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: true,
              selectedVenue: ""
            }
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toHaveProperty('pathToCsvFile', 'http://localhost/bookings/csv?onlyDigitalVenues=true')
        })
      });
    })

    describe('showDownloadButton', () => {
      it('should hide the download button by default', () => {
        // when
        const props = mapStateToProps({})

        // then
        expect(props).toHaveProperty('showDownloadButton', false)
      })

      it('should be displayed when downloading digital venues', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true
          }
        };

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDownloadButton', true)
      })

      it('should be displayed when a venue is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedVenue: 'G2YU',
          }
        };

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDownloadButton', true)
      })

      it('should be displayed when the `all venues` option is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedVenue: 'all',
          }
        };

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDownloadButton', true)
      })
    })
  })
})
