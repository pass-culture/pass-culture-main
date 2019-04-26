import { mapStateToProps } from '../VersoControlContainer'

describe('src | components | verso | verso-controls | VersoControlContainer', () => {
  it('should return a booking and isFinished props', () => {
    // given
    const state = {
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
              stocks: [{ id: 'AB' }, { id: 'BA' }],
              thingId: 'BAFA',
            },
            offerId: 'AE',
          },
        ],
      },
      geolocation: {},
    }
    const router = {
      match: {
        params: { mediationId: 'BA', offerId: 'AE' },
      },
    }

    // when
    const result = mapStateToProps(state, router)

    // then
    expect(result.booking.id).toBe('A9')
    expect(result.isFinished).toBe(false)
  })

  it('should not return a booking if none exist on given stocks', () => {
    // given
    const state = {
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
              stocks: [{ id: 'KA' }, { id: 'AK' }],
              thingId: 'BAFA',
            },
            offerId: 'AE',
          },
        ],
      },
      geolocation: {},
    }
    const router = {
      match: {
        params: { mediationId: 'BA', offerId: 'AE' },
      },
    }

    // when
    const result = mapStateToProps(state, router)

    // then
    expect(result.booking).not.toBeDefined()
    expect(result.isFinished).not.toBeDefined()
  })

  it('should not return a booking if one exists on given stocks but is cancelled', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'A9',
            isCancelled: true,
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
              stocks: [{ id: 'AB' }, { id: 'BA' }],
              thingId: 'BAFA',
            },
            offerId: 'AE',
          },
        ],
      },
      geolocation: {},
    }
    const router = {
      match: {
        params: { mediationId: 'BA', offerId: 'AE' },
      },
    }

    // when
    const result = mapStateToProps(state, router)

    // then
    expect(result.booking).not.toBeDefined()
    expect(result.isFinished).not.toBeDefined()
  })
})
