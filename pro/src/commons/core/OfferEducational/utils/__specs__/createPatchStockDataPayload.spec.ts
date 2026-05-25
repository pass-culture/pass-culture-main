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
          startDate: startDate,
          endDate: endDate,
          eventTime: '12:00',
          numberOfTickets: 11,
          totalPrice: 10,
          bookingLimitDate: bookingDate,
          educationalPriceDetail: 'price detail',
        },
        '56',
        {
          startDate: '',
          endDate: '',
          eventTime: '',
          numberOfTickets: null,
          totalPrice: null,
          bookingLimitDate: '',
          educationalPriceDetail: '',
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

  it('should send both startDatetime and endDatetime when only eventTime is modified', () => {
    const startDate = addDays(new Date(), 2).toISOString().split('T')[0]
    const endDate = addDays(new Date(), 3).toISOString().split('T')[0]
    const bookingDate = addDays(new Date(), 1).toISOString().split('T')[0]

    const initialValues = {
      startDate: startDate,
      endDate: endDate,
      eventTime: '10:00',
      numberOfTickets: 11,
      totalPrice: 10,
      bookingLimitDate: bookingDate,
      educationalPriceDetail: 'price detail',
    }

    const payload = createPatchStockDataPayload(initialValues, '56', {
      ...initialValues,
      eventTime: '11:00',
    })

    expect(payload.startDatetime).toContain(startDate)
    expect(payload.endDatetime).toContain(endDate)
  })
})
