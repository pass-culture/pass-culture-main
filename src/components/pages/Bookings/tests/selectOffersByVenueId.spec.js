import selectOffersByVenueId from '../selectOffersByVenueId'

describe('src | components | pages | Bookings | selectOffersByVenueId', () => {
  it('should return an empty list of offers when state contains no offer', () => {
    // given
    const venueId = "A8HQ"
    const state = {
      data:{
        offers:[]
      }
    }

    // when
    const offersToDisplay = selectOffersByVenueId(venueId, state)

    // then
    expect(offersToDisplay).toEqual([])
  })

  it('should return only the offers whom venueId is equal to the one given', () => {
    // given
    const venueId = "A8HQ"
    const state = {
      data:{
        offers: [
          {
            id:"AVJA",
            venueId: "A8HQ"
          },
          {
            id:"AV9Q",
            venueId: "A8HQ"
          },
          {
            id:"AVGQ",
            venueId: "A8RA"
          }
        ]
      }
    }

    // when
    const offersToDisplay = selectOffersByVenueId(venueId, state)

    // then
    const offerListExpected=[
      {
        id:"AVJA",
        venueId: "A8HQ"
      },
      {
        id:"AV9Q",
        venueId: "A8HQ"
      }
    ]

    expect(offersToDisplay).toEqual(offerListExpected)
  })

  it('should return an empty list of offer when state is not initialized', () => {
    // given
    const venueId = "A8HQ"
    const state = {}

    // when
    const offersToDisplay = selectOffersByVenueId(venueId, state)

    // then
    const offerListExpected=[]

    expect(offersToDisplay).toEqual(offerListExpected)
  })
})
