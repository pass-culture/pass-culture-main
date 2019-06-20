import {mapStateToProps, mapDispatchToProps} from '../FilterByOfferContainer'

describe('src | components | pages | Bookings | FilterByOfferContainer', () => {
  describe('mapDispatchToProps', () => {
    it('enable to filter on a specific offer', () => {
      // when
      const props = mapDispatchToProps()

      // the
      expect(props).toHaveProperty(
        'selectBookingsForOffers'
      )
    })

    it('preserve selected offer', () => {
      // given
      const dispatch = jest.fn()
      const props = mapDispatchToProps(dispatch)

      //when
      props.selectBookingsForOffers('AVJA')

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: 'AVJA',
        type: 'BOOKING_SUMMARY_SELECT_OFFER',
      })
    })
  })

  describe('mapStateToProps', () => {
    it('return only digital offers when isFilterByDigitalVenues is true', () => {
      // given
      const state={
        bookingSummary:{
          isFilterByDigitalVenues: true
        },
        data:{
          offers:[{
            id:"AVJA",
            product:{
              offerType:{
                onlineOnly:true
              }
            }
          },
            {
              id:"AFTA",
              product:{
                offerType:{
                  onlineOnly:false
                }
              }
            }]
        }
      }
      // when
      const props = mapStateToProps(state)

      // then
      expect(props.offersOptions).toEqual(expect.arrayContaining(
        [{
          id:"AVJA",
          product:{
            offerType:{
              onlineOnly:true
            }
          }
        }]
      ))
    })

    it("add 'Toutes les offres' option to the offer options", () => {
      // given
      const state={
        bookingSummary:{
          isFilterByDigitalVenues: true
        },
        data:{
          offers:[{
            id:"AVJA",
            product:{
              offerType:{
                onlineOnly:true
              }
            }
          }]
        }
      }
      // when
      const props = mapStateToProps(state)

      // then
      expect(props.offersOptions).toEqual(expect.arrayContaining(
        [{
          id:"all",
          name: "Toutes les offres"
        }]
      ))
    })

    it("return only non digital offers when isFilterByDigitalVenues is false and venueId is 'all'", () => {
      // given
      const state={
        bookingSummary:{
          isFilterByDigitalVenues:false,
          selectedVenue:'all'
        },
        data:{
          offers:[{
            id:"AVJA",
            product:{
              offerType:{
                onlineOnly:true
              }
            }
          },
            {
              id:"AFTA",
              product:{
                offerType:{
                  onlineOnly:false
                }
              }
            }]
        }
      }
      // when
      const props = mapStateToProps(state)

      // then
      expect(props.offersOptions).toEqual(expect.arrayContaining(
        [{
          id:"AFTA",
          product:{
            offerType:{
              onlineOnly:false
            }
          }
        }]
      ))

      expect(props.offersOptions).toEqual(expect.not.arrayContaining(
        [{
          id:"AVJA",
          product:{
            offerType:{
              onlineOnly:true
            }
          }
        }]
      ))
    })

    it("return offers whom venueId os the one given when venueId is defined", () => {
      // given
      const state={
        bookingSummary:{
          isFilterByDigitalVenues:false,
          selectedVenue:'A8RQ'
        },
        data:{
          offers:[{
            id:"AVJA",
            product:{
              offerType:{
                onlineOnly:true
              }
            },
            venueId: "AHPA"
          },
            {
              id:"AFTA",
              product:{
                offerType:{
                  onlineOnly:false
                }
              },
              venueId: "A8RQ"
            }]
        }
      }
      // when
      const props = mapStateToProps(state)

      // then
      expect(props.offersOptions).toEqual(expect.arrayContaining(
        [{
          id:"AFTA",
          product:{
            offerType:{
              onlineOnly:false
            }
          },
          venueId: "A8RQ"
        }]
      ))
    })
  })
})
