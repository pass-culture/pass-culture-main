import { addDays } from 'date-fns'

import { createPatchStockDataPayload } from '../createPatchStockDataPayload'

describe('createPatchStockDataPayload', () => {
  it('should create a well formatted payload', () => {
    const startDate = addDays(new Date(), 2).toISOString().split('T')[0]
    const endDate = addDays(new Date(), 3).toISOString().split('T')[0]
    const bookingDate = addDays(new Date(), 1).toISOString().split('T')[0]

    expect(
      createPatchStockDataPayload(
        {
          startDatetime: startDate,
          endDatetime: endDate,
          eventTime: '12:00',
          numberOfPlaces: 11,
          totalPrice: 10,
          bookingLimitDatetime: bookingDate,
          priceDetail: 'price detail',
        },
        '56',
        {
          startDatetime: '',
          endDatetime: '',
          eventTime: '',
          numberOfPlaces: null,
          totalPrice: null,
          bookingLimitDatetime: '',
          priceDetail: '',
        }
      )
    ).toEqual({
      bookingLimitDatetime: expect.stringContaining(bookingDate),
      startDatetime: expect.stringContaining(startDate),
      endDatetime: expect.stringContaining(endDate),
      numberOfTickets: 11,
      totalPrice: 10,
      educationalPriceDetail: 'price detail',
    })
  })
})
