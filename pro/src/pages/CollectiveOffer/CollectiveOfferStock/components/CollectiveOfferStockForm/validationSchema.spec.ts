import { addDays, addYears, format, subMinutes } from 'date-fns'

import { CollectiveAdditionalFeeType } from '@/apiClient/adage'
import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import { MAX_PRICE } from '../utils/constants'
import {
  type CollectiveOfferStockFormValues,
  generateValidationSchema,
} from './validationSchema'

describe('validationSchema', () => {
  const values = {
    startDate: '2050-09-01',
    endDate: '2050-09-02',
    bookingLimitDate: '2050-08-31',
    eventTime: '14:00',
    numberOfTickets: 56,
    numberOfTeachers: 5,
    servicePrice: 5,
    hasAdditionalFees: false,
    collectiveAdditionalFees: [],
  }

  it.each([
    {
      description: 'should require mandatory fields',
      initialState: {},
      formValues: {},
      expectedErrors: [
        'La date de début est obligatoire',
        'La date de fin est obligatoire',
        'L’horaire est obligatoire',
        "Le nombre d'élèves est obligatoire",
        "Le nombre d'accompagnateurs est obligatoire",
        'La date limite de réservation est obligatoire',
        'Le tarif de la prestation est obligatoire',
        'Veuillez choisir une option',
      ],
    },
    {
      description: 'start and end date should be on same school year',
      initialState: {},
      formValues: {
        ...values,
        endDate: addYears(values.startDate, 2).toISOString().split('T')[0],
      },
      expectedErrors: ['Les dates doivent être sur la même année scolaire'],
    },
    {
      description:
        'should allow a start datetime set on 01/09/N and an end datetime set on 31/08/N+1',
      initialState: {},
      formValues: {
        ...values,
        startDate: '2050-09-01',
        endDate: '2051-08-31',
      },
      expectedErrors: [],
    },
    {
      description: 'booking datetime should not be after start datetime',
      initialState: {},
      formValues: {
        ...values,
        bookingLimitDate: addDays(values.startDate, 1)
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
      initialState: {},
      formValues: {
        ...values,
        startDate: new Date().toISOString().split('T')[0],
        endDate: addDays(new Date(), 2).toISOString().split('T')[0],
        bookingLimitDate: new Date().toISOString().split('T')[0],
        eventTime: format(subMinutes(new Date(), 1), 'HH:mm'),
      },
      expectedErrors: ["L'horaire doit être postérieur à l'heure actuelle"],
    },
    {
      description: 'booking limit date should not be in the past',
      initialState: {},
      formValues: {
        ...values,
        bookingLimitDate: '2024-08-31T13:00:00Z',
      },
      expectedErrors: [
        'La date limite de réservation doit être égale ou postérieure à la date actuelle',
      ],
    },
    {
      description:
        'booking limit date can be in the past if the form is read only',
      initialState: { canEditDates: false },
      formValues: {
        ...values,
        bookingLimitDate: '2024-08-31T13:00:00Z',
      },
      expectedErrors: [],
    },
    {
      description:
        'bookingLimitDate: la règle ne s’applique pas si CAN_EDIT_DATES=false',
      initialState: { canEditDates: false },
      formValues: {
        ...values,
        bookingLimitDate: '2000-01-01',
      },
      expectedErrors: [],
    },
    {
      description: 'number of participants should be at least 1',
      initialState: {},
      formValues: {
        ...values,
        numberOfTickets: 0,
      },
      expectedErrors: ['Minimum 1 élève'],
    },
    {
      description: 'number of participants should not exceed 3000',
      initialState: {},
      formValues: {
        ...values,
        numberOfTickets: 3001,
      },
      expectedErrors: ["Le nombre d'élèves ne doit pas dépasser 3000"],
    },
    {
      description: 'numberOfTickets should be an integer',
      initialState: {},
      formValues: { ...values, numberOfTickets: 12.5 },
      expectedErrors: ['Nombre entier attendu'],
    },
    {
      description: 'number of teachers should be at least 0',
      initialState: {},
      formValues: {
        ...values,
        numberOfTeachers: -1,
      },
      expectedErrors: ['Minimum 0 accompagnateur'],
    },
    {
      description: 'number of teachers should not exceed 50',
      initialState: {},
      formValues: {
        ...values,
        numberOfTeachers: 51,
      },
      expectedErrors: ["Le nombre d'accompagnateurs ne doit pas dépasser 50"],
    },
    {
      description: 'numberOfTeachers should be an integer',
      initialState: {},
      formValues: { ...values, numberOfTeachers: 12.5 },
      expectedErrors: ['Nombre entier attendu'],
    },
    {
      description:
        'should require additional fees when hasAdditionalFees is true',
      initialState: {},
      formValues: {
        ...values,
        hasAdditionalFees: true,
      },
      expectedErrors: ['Ajoutez au moins un type de frais annexes'],
    },
    {
      description: 'should reject an additional fee with an invalid type',
      initialState: {},
      formValues: {
        ...values,
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: 'INVALID_TYPE' as CollectiveAdditionalFeeType,
            amount: 10,
            label: null,
          },
        ],
      },
      expectedErrors: ['Type de frais annexe invalide'],
    },
    {
      description: 'additional fees amounts should be positive',
      initialState: {},
      formValues: {
        ...values,
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.MEAL,
            amount: -1,
            label: null,
          },
        ],
      },
      expectedErrors: ['Le prix du frais annexe doit être supérieur à 0.01'],
    },
    {
      description: 'additional fees types should not be duplicated',
      initialState: {},
      formValues: {
        ...values,
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.MEAL,
            amount: 1,
            label: null,
          },
          {
            type: CollectiveAdditionalFeeType.MEAL,
            amount: 2,
            label: null,
          },
        ],
      },
      expectedErrors: [
        'Certains types sont en doubles',
        'Certains labels sont en doubles',
      ],
    },
    {
      description: 'additional fees labels should not be duplicated',
      initialState: {},
      formValues: {
        ...values,
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.OTHER,
            amount: 1,
            label: 'Ceci est un Label dupliqué',
          },
          {
            type: CollectiveAdditionalFeeType.OTHER,
            amount: 2,
            label: 'Ceci est UN label dupliqué',
          },
        ],
      },
      expectedErrors: ['Certains labels sont en doubles'],
    },
    {
      description: 'additional fees labels should not be existing types labels',
      initialState: {},
      formValues: {
        ...values,
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.COPYRIGHT,
            amount: 1,
            label: null,
          },
          {
            type: CollectiveAdditionalFeeType.OTHER,
            amount: 2,
            label: "Droits d'auteur",
          },
        ],
      },
      expectedErrors: ['Certains labels sont en doubles'],
    },
    {
      description: 'servicePrice should not exceed 60000€',
      initialState: {},
      formValues: { ...values, servicePrice: 60001 },
      expectedErrors: [
        'Le tarif de la prestation ne doit pas dépasser 60000 €',
      ],
    },
    {
      description: 'servicePrice should be positive',
      initialState: {},
      formValues: { ...values, servicePrice: -15 },
      expectedErrors: ['Nombre positif attendu'],
    },
    {
      description: `price should should be less than ${MAX_PRICE}`,
      initialState: {},
      formValues: {
        ...values,
        servicePrice: 59_999,
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.MEAL,
            amount: 2,
            label: null,
          },
          {
            type: CollectiveAdditionalFeeType.TRAVEL,
            amount: 1,
            label: null,
          },
        ],
      },
      expectedErrors: [
        // The error is on the servicePrice and on the collectiveAdditionalFees fields
        `Le prix total ne doit pas dépasser ${MAX_PRICE} €`,
        `Le prix total ne doit pas dépasser ${MAX_PRICE} €`,
      ],
    },
  ])(`$description`, async ({
    initialState: {
      canEditDetails = true,
      canEditDates = true,
      canEditDiscount = true,
      initialPrice = null,
    },
    formValues,
    expectedErrors,
  }: {
    description: string
    initialState: {
      canEditDetails?: boolean
      canEditDates?: boolean
      canEditDiscount?: boolean
      initialPrice?: number | null
    }
    formValues: Partial<CollectiveOfferStockFormValues>
    expectedErrors: string[]
  }) => {
    const errors = await getYupValidationSchemaErrors(
      generateValidationSchema(
        canEditDetails,
        canEditDates,
        canEditDiscount,
        initialPrice
      ),
      formValues
    )
    expect(errors).toEqual(expectedErrors)
  })
})
