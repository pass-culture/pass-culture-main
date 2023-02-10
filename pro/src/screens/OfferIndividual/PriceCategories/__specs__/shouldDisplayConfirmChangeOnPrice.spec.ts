import { IOfferIndividualStock } from 'core/Offers/types'
import { individualStockFactory } from 'utils/individualApiFactories'

import { priceCategoryFormFactory } from '../form/factories'
import { PriceCategoriesFormValues } from '../form/types'
import { shouldDisplayConfirmChangeOnPrice } from '../PriceCategories'

describe('shouldDisplayConfirmChangeOnPrice', () => {
  const cases: {
    description: string
    stocks: IOfferIndividualStock[]
    initialValues: PriceCategoriesFormValues
    values: PriceCategoriesFormValues
    expected: boolean
  }[] = [
    {
      description: 'nothing has been modified',
      stocks: [individualStockFactory()],
      initialValues: {
        priceCategories: [],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory()],
        isDuo: true,
      },
      expected: false,
    },
    {
      description: 'there is no stock',
      stocks: [],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory()],
        isDuo: true,
      },
      expected: false,
    },
    {
      description: 'there is no price category associated with stock',
      stocks: [individualStockFactory()],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory()],
        isDuo: true,
      },
      expected: false,
    },
    {
      description: 'price category was just created',
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
      expected: false,
    },
    {
      description:
        'there is price category associated with stock and change on label',
      stocks: [individualStockFactory({ priceCategoryId: 42 })],
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
      expected: false,
    },
    {
      description:
        'there is no price category associated with stock and change on price',
      stocks: [individualStockFactory({ priceCategoryId: 666 })],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ id: 42, price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: 42 })],
        isDuo: true,
      },
      expected: false,
    },
    {
      description:
        'there is price category associated with stock and change on price',
      stocks: [individualStockFactory({ priceCategoryId: 42 })],
      initialValues: {
        priceCategories: [priceCategoryFormFactory({ id: 42, price: 3.14 })],
        isDuo: true,
      },
      values: {
        priceCategories: [priceCategoryFormFactory({ id: 42 })],
        isDuo: true,
      },
      expected: true,
    },
  ]
  cases.forEach(({ description, stocks, initialValues, values, expected }) => {
    it(`should retrun expected value when ${description}`, () => {
      const result = shouldDisplayConfirmChangeOnPrice(
        stocks,
        initialValues,
        values
      )

      expect(result).toBe(expected)
    })
  })
})
