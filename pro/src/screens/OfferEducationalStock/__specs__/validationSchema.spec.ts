import { OfferEducationalStockFormValues } from 'core/OfferEducational/types'
import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { generateValidationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const values = {
    startDatetime: '2024-09-01',
    endDatetime: '2024-09-01',
    bookingLimitDatetime: '2024-09-01',
    eventTime: '14:00',
    numberOfPlaces: 56,
    priceDetail: 'Détails sur le prix',
    totalPrice: 1500,
  }

  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2024-09-01T13:00:00Z'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  const cases: {
    description: string
    formValues: Partial<OfferEducationalStockFormValues>
    expectedErrors: string[]
  }[] = [
    {
      description: 'start and end date should be on same school year',
      formValues: {
        ...values,
        startDatetime: '2024-09-01',
        endDatetime: '2025-09-01',
      },
      expectedErrors: ['Les dates doivent être sur la même année scolaire'],
    },
    {
      description:
        'should allow a start datetime set on 01/09/N and an end datetime set on 31/08/N+1',
      formValues: {
        ...values,
        startDatetime: '2024-09-01',
        endDatetime: '2025-08-31',
      },
      expectedErrors: [],
    },
    {
      description: 'booking datetime should not be after start datetime',
      formValues: {
        ...values,
        startDatetime: '2024-09-01',
        bookingLimitDatetime: '2024-09-02',
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
        eventTime: '11:00',
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
  ]

  cases.forEach(({ description, formValues, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        generateValidationSchema(false, 0),
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})
