import { markAsBooked } from '../markBookingsAsBooked'

describe('markAsBooked', () => {
  it('should indicate that user has booked stock when matching booking is found', () => {
    // given
    const bookings = [
      {
        stockId: 'DU',
      },
    ]

    const stocksToMark = [
      {
        id: 'DU',
      },
    ]
    // when
    const results = markAsBooked(bookings)(stocksToMark)

    // then
    expect(results).toStrictEqual([
      {
        id: 'DU',
        userHasAlreadyBookedThisDate: true,
      },
    ])
  })

  it('should indicate that user has not booked stock when no matching booking is found', () => {
    // given
    const bookings = [
      {
        stockId: 'ZZ',
      },
    ]

    const stocksToMark = [
      {
        id: 'DU',
      },
    ]
    // when
    const results = markAsBooked(bookings)(stocksToMark)

    // then
    expect(results).toStrictEqual([
      {
        id: 'DU',
        userHasAlreadyBookedThisDate: false,
      },
    ])
  })

  it('should indicate that user has not booked stock when no bookings', () => {
    const stocksToMark = [
      {
        id: 'DU',
      },
    ]

    // when
    const results = markAsBooked([])(stocksToMark)

    // then
    expect(results).toStrictEqual([
      {
        id: 'DU',
        userHasAlreadyBookedThisDate: false,
      },
    ])
  })
})
