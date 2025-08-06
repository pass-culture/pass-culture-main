import { addDays, subDays } from 'date-fns'

import { getYupValidationSchemaErrors } from 'commons/utils/yupValidationTestHelpers'

import { EditStockFormValues } from '../StocksCalendarTableEditStock'
import { validationSchema } from '../validationSchema'

describe('validationSchema for StocksCalendarTableEditStock', () => {
  const defaultValues: EditStockFormValues = {
    date: addDays(new Date(), 2).toISOString().split('T')[0],
    bookingLimitDate: addDays(new Date(), 1).toISOString().split('T')[0],
    remainingQuantity: 12,
    priceCategory: '1',
    time: '12:12',
  }

  const cases: {
    description: string
    formValues: EditStockFormValues
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form for normal stock',
      formValues: defaultValues,
      expectedErrors: [],
    },
    {
      description: 'invalidate form for beginning date in the past',
      formValues: {
        ...defaultValues,
        date: subDays(new Date(), 2).toISOString().split('T')[0],
      },
      expectedErrors: [
        'L’évènement doit être à venir',
        "La date limite de réservation ne peut être postérieure à la date de début de l'évènement",
      ],
    },
    {
      description: 'invalidate form for invalid beginning date',
      formValues: {
        ...defaultValues,
        date: '',
      },
      expectedErrors: [
        'L’évènement doit être à venir',
        'La date est obligatoire.',
      ],
    },
    {
      description: 'invalidate form for invalid time',
      formValues: {
        ...defaultValues,
        time: '',
      },
      expectedErrors: ["L'horaire est obligatoire."],
    },
    {
      description: 'invalidate form for invalid price category',
      formValues: {
        ...defaultValues,
        priceCategory: '',
      },
      expectedErrors: ['Le tarif est obligatoire.'],
    },
    {
      description: 'invalidate form for invalid booking limit date',
      formValues: {
        ...defaultValues,
        bookingLimitDate: '',
      },
      expectedErrors: ['La date limite de réservation est obligatorie.'],
    },
    {
      description: 'invalidate form for negative remaining quantity',
      formValues: {
        ...defaultValues,
        remainingQuantity: -1,
      },
      expectedErrors: ['Veuillez indiquer une quantité positive'],
    },
    {
      description:
        'invalidate form for remaining quantity superior to one million',
      formValues: {
        ...defaultValues,
        remainingQuantity: 1_000_000_000_000,
      },
      expectedErrors: [
        'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million',
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
