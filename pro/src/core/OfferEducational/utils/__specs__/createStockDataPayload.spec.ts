import {
  EducationalOfferType,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational/types'

import { createStockDataPayload } from '../createStockDataPayload'

const offerId = 55
const departmentCode = '56'

describe('createStockDataPayload', () => {
  it('should return valid payload when form values are provided', () => {
    const values: OfferEducationalStockFormValues = {
      bookingLimitDatetime: '2024-06-30',
      educationalOfferType: EducationalOfferType.CLASSIC,
      endDatetime: '2024-06-30',
      eventTime: '04:15',
      numberOfPlaces: 400,
      priceDetail: 'some price details',
      startDatetime: '2024-06-30',
      totalPrice: 450,
    }

    expect(createStockDataPayload(values, departmentCode, offerId)).toEqual({
      bookingLimitDatetime: '2024-06-30T02:15:00Z',
      educationalPriceDetail: 'some price details',
      endDatetime: '2024-06-30T02:15:00Z',
      numberOfTickets: 400,
      offerId: 55,
      startDatetime: '2024-06-30T02:15:00Z',
      totalPrice: 450,
    })
  })
})
