import { mapStateToProps } from '../VersoControlContainer'

describe('src | components | verso | verso-controls | VersoControlContainer', () => {
  let state
  let router

  beforeEach(() => {
    state = {
      data: {
        bookings: [
          {
            id: 'A9',
            isUsed: false,
            recommendationId: 'AGQA',
            stockId: 'AB',
          },
        ],
        recommendations: [
          {
            bookingsIds: ['A9'],
            id: 'AGQA',
            mediationId: 'BA',
            offer: {
              isFinished: false,
              productId: 'BAFA',
              stocks: [{ id: 'AB' }, { id: 'BA' }],
              venue: {
                latitude: 48.91683,
                longitude: 2.4388,
              },
            },
            offerId: 'AE',
          },
        ],
      },
      geolocation: {},
    }
    router = {
      match: {
        params: { mediationId: 'BA', offerId: 'AE' },
      },
    }
  })

  it('should return a booking and isFinished props when booking is not cancelled and matches stock ', () => {
    // when
    const result = mapStateToProps(state, router)

    // then
    expect(result.booking.id).toBe('A9')
    expect(result.isFinished).toBe(false)
  })

  it('should not return a booking if none exists on given stocks', () => {
    // given
    state.data.bookings[0].stockId = 'AB'
    state.data.recommendations[0].offer.stocks = [{ id: 'KA' }, { id: 'AK' }]

    // when
    const result = mapStateToProps(state, router)

    // then
    expect(result.booking).not.toBeDefined()
    expect(result.isFinished).not.toBeDefined()
  })

  it('should not return a booking if one exists on given stocks but is cancelled', () => {
    // given
    state.data.bookings[0].isCancelled = true

    // when
    const result = mapStateToProps(state, router)

    // then
    expect(result.booking).not.toBeDefined()
    expect(result.isFinished).not.toBeDefined()
  })
})
