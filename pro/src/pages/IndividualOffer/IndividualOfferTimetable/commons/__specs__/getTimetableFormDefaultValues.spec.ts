import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from '@/commons/utils/factories/individualApiFactories'

import { getTimetableFormDefaultValues } from '../getTimetableFormDefaultValues'

const defaultOpeningHours: WeekdayOpeningHoursTimespans = {
  MONDAY: null,
  TUESDAY: null,
  WEDNESDAY: null,
  THURSDAY: null,
  FRIDAY: null,
  SATURDAY: null,
  SUNDAY: null,
}

const defualtOffer = getIndividualOfferFactory({
  priceCategories: [{ id: 1, label: 'Tarif 1', price: 12 }],
})

describe('getTimetableFormDefaultValues', () => {
  it('should get the default values for an empty form in creation mode', () => {
    expect(
      getTimetableFormDefaultValues({
        openingHours: defaultOpeningHours,
        stocks: [],
        offer: defualtOffer,
      })
    ).toEqual(
      expect.objectContaining({
        openingHours: defaultOpeningHours,
        quantityPerPriceCategories: [{ priceCategory: '1' }],
        timetableType: 'calendar',
      })
    )
  })

  it('should set the initial form as calendar type if there are stocks already', () => {
    expect(
      getTimetableFormDefaultValues({
        openingHours: defaultOpeningHours,
        stocks: [
          getOfferStockFactory({ id: 1 }),
          getOfferStockFactory({ id: 2 }),
        ],
        offer: defualtOffer,
      })
    ).toEqual(
      expect.objectContaining({
        timetableType: 'calendar',
      })
    )
  })

  it('should set the initial form as openingHours type if there are non-empty openingHours already', () => {
    expect(
      getTimetableFormDefaultValues({
        openingHours: { ...defaultOpeningHours, MONDAY: [['12:12', '15:15']] },
        stocks: [getOfferStockFactory({ id: 1 })],
        offer: defualtOffer,
      })
    ).toEqual(
      expect.objectContaining({
        timetableType: 'openingHours',
      })
    )
  })
})
