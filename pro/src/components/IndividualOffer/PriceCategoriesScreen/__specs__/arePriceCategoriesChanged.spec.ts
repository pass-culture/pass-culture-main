import { priceCategoryFormFactory } from '@/commons/utils/factories/priceCategoryFactories'

import { PriceCategoriesFormValues } from '../form/types'
import { arePriceCategoriesChanged } from '../PriceCategoriesScreen'

describe('arePriceCategoriesChanged', () => {
  const cases: {
    description: string
    initialValues: PriceCategoriesFormValues
    values: PriceCategoriesFormValues
    expected: boolean
  }[] = [
    {
      description: 'nothing has been modified',
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
      description: 'price category was just created',
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
      description: 'there is change on label (not on price)',
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
      description: 'there is change on price',
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
  cases.forEach(({ description, initialValues, values, expected }) => {
    it(`should return expected value when ${description}`, () => {
      const result = arePriceCategoriesChanged(initialValues, values)

      expect(result).toBe(expected)
    })
  })
})
