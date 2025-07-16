import {
  priceCategoriesFormValuesFactory,
  priceCategoryFormFactory,
} from 'commons/utils/factories/priceCategoryFactories'
import { getYupValidationSchemaErrors } from 'commons/utils/yupValidationTestHelpers'

import { PRICE_CATEGORY_LABEL_MAX_LENGTH, PRICE_CATEGORY_PRICE_MAX } from '../constants'
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
      expectedErrors: ['Le formulaire n’est pas complet'],
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
        'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix',
        'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix',
      ],
    },
    {
      description: 'duplicated label and price',
      formValues: priceCategoriesFormValuesFactory({
        priceCategories: [
          priceCategoryFormFactory({ label: 'Tarif', price: 10 }),
          priceCategoryFormFactory({ label: 'Tarif', price: 10 }),
        ],
      }),
      expectedErrors: [
        'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix',
        'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix',
      ],
    },
    {
      description: 'missing label',
      formValues: priceCategoriesFormValuesFactory({
        priceCategories: [priceCategoryFormFactory({ label: '' })],
      }),
      expectedErrors: ['Veuillez renseigner un intitulé de tarif'],
    },
    {
      description: 'label too long',
      formValues: priceCategoriesFormValuesFactory({
        priceCategories: [
          priceCategoryFormFactory({
            label: 'a'.repeat(PRICE_CATEGORY_LABEL_MAX_LENGTH + 1),
          }),
        ],
      }),
      expectedErrors: ['Le nom du tarif est trop long'],
    },
    {
      description: 'missing price',
      formValues: priceCategoriesFormValuesFactory({
        priceCategories: [priceCategoryFormFactory({ price: undefined })],
      }),
      expectedErrors: ['Veuillez renseigner un tarif'],
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
