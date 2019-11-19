import { markAsCancelled } from '../markAsCancelled'

describe('markAsCancelled', () => {
  it('should return userHasCancelledThisDate as true when the booking has been cancelled', () => {
    // given
    const bookings = [
      {
        id: 'HQ',
        isCancelled: true,
        modelName: 'Booking',
        recommendation: {},
        stock: {
          id: 'DU',
          modelName: 'Stock',
          offerId: 'CQ',
        },
      },
      {
        id: 'HY',
        isCancelled: false,
        modelName: 'Booking',
        recommendation: {},
        stock: {
          id: 'DQ',
          modelName: 'Stock',
          offerId: 'CQ',
        },
      },
    ]

    const items = [
      {
        id: 'DU',
        modelName: 'Stock',
        offerId: 'CQ',
        price: 23,
        userHasAlreadyBookedThisDate: true,
      },
    ]

    // when
    const results = markAsCancelled(bookings)(items)

    // then
    expect(results[0].userHasAlreadyBookedThisDate).toBe(true)
  })
})
