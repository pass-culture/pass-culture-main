import { IOfferIndividualStock } from 'core/Offers/types'
import { individualStockFactory } from 'utils/individualApiFactories'

import { priceCategoryFormFactory } from '../form/factories'
import { PriceCategoriesFormValues } from '../form/types'
import { POPIN_TYPE, getPopinType } from '../PriceCategories'

describe('getPopinType', () => {
  const cases: {
    description: string
    stocks: IOfferIndividualStock[]
    initialValues: PriceCategoriesFormValues
    values: PriceCategoriesFormValues
    expected: POPIN_TYPE | null
  }[] = [
    {
      description: '1 nothing has been modified',
      stocks: [individualStockFactory()],
      initialValues: {
        priceCategories: [],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory()],
        isDuo: true,
      },
      expected: null,
    },
    {
      description: '2 there is no stock',
      stocks: [],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory()],
        isDuo: true,
      },
      expected: null,
    },
    {
      description: '3 there is no price category associated with stock',
      stocks: [individualStockFactory()],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory()],
        isDuo: true,
      },
      expected: null,
    },
    {
      description: '4 price category was just created',
      stocks: [individualStockFactory({ priceCategoryId: 42 })],
      initialValues: {
        priceCategories: [
          priceCategoryFormFactory({ id: undefined, price: 3.14 }),
        ],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: undefined })],
        isDuo: true,
      },
      expected: null,
    },
    {
      description:
        '5 there is price category associated with stock and change on label (not on price)',
      stocks: [
        individualStockFactory({ priceCategoryId: 42, bookingsQuantity: 0 }),
      ],
      initialValues: {
        priceCategories: [
          priceCategoryFormFactory({
            id: 42,
            price: 3.14,
            label: 'another label in the wall',
          }),
        ],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: 42, price: 3.14 })],
        isDuo: true,
      },
      expected: null,
    },
    {
      description:
        '6 there is no price category associated with stock and change on price',
      stocks: [individualStockFactory({ priceCategoryId: 666 })],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ id: 42, price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: 42 })],
        isDuo: true,
      },
      expected: null,
    },
    {
      description:
        '7 there is price category associated with stock, no bookings and change on price',
      stocks: [
        individualStockFactory({ priceCategoryId: 42, bookingsQuantity: 0 }),
        individualStockFactory({ priceCategoryId: 1337, bookingsQuantity: 10 }),
      ],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ id: 42, price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: 42 })],
        isDuo: true,
      },
      expected: POPIN_TYPE.PRICE,
    },
    {
      description:
        '8 there is price category associated with stock, bookings and change on price',
      stocks: [
        individualStockFactory({ priceCategoryId: 42, bookingsQuantity: 1 }),
      ],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ id: 42, price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: 42 })],
        isDuo: true,
      },
      expected: POPIN_TYPE.PRICE_WITH_BOOKING,
    },
    {
      description:
        '9 there is price category associated with stock, no bookings and change on label',
      stocks: [
        individualStockFactory({ priceCategoryId: 42, bookingsQuantity: 0 }),
      ],
      initialValues: {
        priceCategories: [
          priceCategoryFormFactory({ id: 42, label: 'a new super label' }),
        ],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: 42 })],
        isDuo: true,
      },
      expected: null,
    },
  ]
  cases.forEach(({ description, stocks, initialValues, values, expected }) => {
    it(`should return expected value when ${description}`, () => {
      const result = getPopinType(stocks, initialValues, values)

      expect(result).toBe(expected)
    })
  })
})
