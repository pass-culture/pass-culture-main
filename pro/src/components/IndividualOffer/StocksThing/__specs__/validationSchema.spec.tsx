import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { stockThingFormValuesFactory } from 'commons/utils/factories/stockThingFormValuesFactories'
import { getYupValidationSchemaErrors } from 'commons/utils/yupValidationTestHelpers'

import { StockThingFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const cases: {
    mode?: OFFER_WIZARD_MODE
    description: string
    formValues: Partial<StockThingFormValues>
    expectedErrors: string[]
    bookingsQuantity: number
  }[] = [
    {
      description: 'valid form',
      formValues: stockThingFormValuesFactory(),
      expectedErrors: [],
      bookingsQuantity: 0,
    },
    {
      description: 'need price',
      formValues: {},
      expectedErrors: ['Veuillez renseigner un prix'],
      bookingsQuantity: 0,
    },

    {
      description: 'price above 300',
      formValues: { price: 300.01 },
      expectedErrors: ['Veuillez renseigner un prix inférieur à 300€'],
      bookingsQuantity: 0,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      description: 'in creation, quantity below 1',
      formValues: { quantity: 0, price: 0 },
      expectedErrors: ['Veuillez indiquer un nombre supérieur à 0'],
      bookingsQuantity: 0,
    },
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      description: 'in edition, quantity below 0',
      formValues: { stockId: 1, quantity: -1, price: 0 },
      expectedErrors: ['Doit être positif'],
      bookingsQuantity: 0,
    },
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      description: 'in edition, quantity below bookings number',
      formValues: { stockId: 1, quantity: 1, price: 0 },
      expectedErrors: [
        'Veuillez indiquer un nombre supérieur ou égal au nombre de réservations',
      ],
      bookingsQuantity: 2,
    },
  ]

  cases.forEach(
    ({
      mode = OFFER_WIZARD_MODE.CREATION,
      description,
      formValues,
      expectedErrors,
      bookingsQuantity,
    }) => {
      it(`should validate the form for case: ${description}`, async () => {
        const errors = await getYupValidationSchemaErrors(
          getValidationSchema(mode, bookingsQuantity, formValues.stockId),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    }
  )
})
