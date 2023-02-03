import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { PRICE_CATEGORY_PRICE_MAX } from '../constants'
import {
  priceCategoriesFormValuesFactory,
  priceCategoryFormFactory,
} from '../factories'
import { PriceCategoriesFormValues } from '../types'
import { validationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: Partial<PriceCategoriesFormValues>
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form',
      formValues: priceCategoriesFormValuesFactory(),
      expectedErrors: [],
    },
    {
      description: 'partial form',
      formValues: { priceCategories: [priceCategoryFormFactory()] },
      expectedErrors: ["Le formulaire n'est pas complet"],
    },
    {
      description: 'negative price',
      formValues: priceCategoriesFormValuesFactory({
        priceCategories: [priceCategoryFormFactory({ price: -1 })],
      }),
      expectedErrors: ['Le prix ne peut pas être inferieur à 0€'],
    },
    {
      description: 'price too high',
      formValues: priceCategoriesFormValuesFactory({
        priceCategories: [priceCategoryFormFactory({ price: 1000 })],
      }),
      expectedErrors: [
        `Veuillez renseigner un tarif inférieur à ${PRICE_CATEGORY_PRICE_MAX}€`,
      ],
    },
    {
      description: 'labels are duplicated',
      formValues: priceCategoriesFormValuesFactory({
        priceCategories: [
          priceCategoryFormFactory({ label: 'Tarif 1' }),
          priceCategoryFormFactory({ label: 'Tarif 2' }),
          priceCategoryFormFactory({ label: 'Tarif 1' }),
        ],
      }),
      expectedErrors: [
        'Veuillez renseigner des intitulés différents',
        'Veuillez renseigner des intitulés différents',
      ],
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        validationSchema,
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})
