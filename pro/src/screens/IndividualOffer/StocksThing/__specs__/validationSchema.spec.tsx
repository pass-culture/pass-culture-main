import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { stockThingFactory } from '../stockThingFactory'
import { StockThingFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: Partial<StockThingFormValues>
    expectedErrors: string[]
    minQuantity: null | number
  }[] = [
    {
      description: 'valid form',
      formValues: stockThingFactory(),
      expectedErrors: [],
      minQuantity: null,
    },
    {
      description: 'need price',
      formValues: {},
      expectedErrors: ['Veuillez renseigner un prix'],
      minQuantity: null,
    },

    {
      description: 'price above 300',
      formValues: { price: 300.01 },
      expectedErrors: ['Veuillez renseigner un prix inférieur à 300€'],
      minQuantity: null,
    },
    {
      description: 'bad quantity',
      formValues: { quantity: 10, price: 0 },
      expectedErrors: ['Quantité trop faible'],
      minQuantity: 20,
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors, minQuantity }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        getValidationSchema(minQuantity),
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})
