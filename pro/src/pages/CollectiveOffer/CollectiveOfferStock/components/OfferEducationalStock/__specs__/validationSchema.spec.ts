import { addDays, addYears, format, subMinutes } from 'date-fns'

import { OfferEducationalStockFormValues } from '@/commons/core/OfferEducational/types'
import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import { generateValidationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const values = {
    startDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
    endDatetime: addDays(new Date(), 3).toISOString().split('T')[0],
    bookingLimitDatetime: addDays(new Date(), 1).toISOString().split('T')[0],
    eventTime: '14:00',
    numberOfPlaces: 56,
    priceDetail: 'Détails sur le prix',
    totalPrice: 1500,
  }

  const cases: {
    description: string
    formValues: Partial<OfferEducationalStockFormValues>
    expectedErrors: string[]
    isReadOnly?: boolean
    preventPriceIncrease?: boolean
  }[] = [
    {
      description: 'start and end date should be on same school year',
      formValues: {
        ...values,
        endDatetime: addYears(values.startDatetime, 2)
          .toISOString()
          .split('T')[0],
      },
      expectedErrors: ['Les dates doivent être sur la même année scolaire'],
    },
    {
      description:
        'should allow a start datetime set on 01/09/N and an end datetime set on 31/08/N+1',
      formValues: {
        ...values,
        startDatetime: '2050-09-01',
        endDatetime: '2051-08-31',
      },
      expectedErrors: [],
    },
    {
      description: 'booking datetime should not be after start datetime',
      formValues: {
        ...values,
        bookingLimitDatetime: addDays(values.startDatetime, 1)
          .toISOString()
          .split('T')[0],
      },
      expectedErrors: [
        'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
      ],
    },
    {
      description:
        'event time should be after current time when start date is today',
      formValues: {
        ...values,
        startDatetime: new Date().toISOString().split('T')[0],
        endDatetime: addDays(new Date(), 2).toISOString().split('T')[0],
        bookingLimitDatetime: new Date().toISOString().split('T')[0],
        eventTime: format(subMinutes(new Date(), 1), 'HH:mm'),
      },
      expectedErrors: ["L'heure doit être postérieure à l'heure actuelle"],
    },
    {
      description: 'number of participants should be at least 1',
      formValues: {
        ...values,
        numberOfPlaces: 0,
      },
      expectedErrors: ['Minimum 1 participant'],
    },
    {
      description: 'number of participants should not exceed 3000',
      formValues: {
        ...values,
        numberOfPlaces: 3001,
      },
      expectedErrors: ['Le nombre de participants ne doit pas dépasser 3000'],
    },
    {
      description: 'price should be at least 0',
      formValues: {
        ...values,
        totalPrice: -1,
      },
      expectedErrors: ['Nombre positif attendu'],
    },
    {
      description: 'price should not exceed 60000',
      formValues: {
        ...values,
        totalPrice: 60001,
      },
      expectedErrors: ['Le prix ne doit pas dépasser 60 000€'],
    },
    {
      description: 'booking limit date should not be in the past',
      formValues: {
        ...values,
        bookingLimitDatetime: '2024-08-31T13:00:00Z',
      },
      expectedErrors: [
        'La date limite de réservation doit être égale ou postérieure à la date actuelle',
      ],
    },
    {
      description:
        'booking limit date can be in the past if the form is read only',
      formValues: {
        ...values,
        bookingLimitDatetime: '2024-08-31T13:00:00Z',
      },
      expectedErrors: [],
      isReadOnly: true,
    },
    {
      description:
        'bookingLimitDatetime: la règle ne s’applique pas si preventPriceIncrease=true',
      formValues: {
        ...values,
        bookingLimitDatetime: '2000-01-01',
      },
      expectedErrors: [],
      isReadOnly: false,
      preventPriceIncrease: true,
    },
    {
      description:
        'bookingLimitDatetime: la règle s’applique si preventPriceIncrease=false',
      formValues: {
        ...values,
        bookingLimitDatetime: '2000-01-01',
      },
      expectedErrors: [
        'La date limite de réservation doit être égale ou postérieure à la date actuelle',
      ],
      isReadOnly: false,
      preventPriceIncrease: false,
    },
  ]

  cases.forEach(
    ({
      description,
      formValues,
      expectedErrors,
      isReadOnly = false,
      preventPriceIncrease = false,
    }) => {
      it(`should validate the form for case: ${description}`, async () => {
        const errors = await getYupValidationSchemaErrors(
          generateValidationSchema(preventPriceIncrease, 0, isReadOnly),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    }
  )
})
