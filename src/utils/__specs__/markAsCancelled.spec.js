import { markAsCancelled } from '../markAsCancelled'

describe('markAsCancelled', () => {
  it('should return userHasCancelledThisDate as true when the booking has been cancelled', () => {
    // given
    const bookings = [
      {
        stockId: 'DU',
        isCancelled: true,
      },
    ]

    const stocks = [
      {
        id: 'DU',
      },
    ]

    // when
    const results = markAsCancelled(bookings)(stocks)

    // then
    expect(results).toStrictEqual([
      {
        id: 'DU',
        userHasCancelledThisDate: true,
      },
    ])
  })

  it('should return userHasCancelledThisDate as false when the booking has not been cancelled', () => {
    // given
    const bookings = [
      {
        stockId: 'DU',
        isCancelled: false,
      },
    ]

    const stocks = [
      {
        id: 'DU',
      },
    ]

    // when
    const results = markAsCancelled(bookings)(stocks)

    // then
    expect(results).toStrictEqual([
      {
        id: 'DU',
        userHasCancelledThisDate: false,
      },
    ])
  })

  it('should return userHasCancelledThisDate as false when no booking', () => {
    // given
    const bookings = []

    const stocks = [
      {
        id: 'DU',
      },
    ]

    // when
    const results = markAsCancelled(bookings)(stocks)

    // then
    expect(results).toStrictEqual([
      {
        id: 'DU',
        userHasCancelledThisDate: false,
      },
    ])
  })
})
