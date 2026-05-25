import { addDays, addYears, format, subMinutes } from 'date-fns'

import { CollectiveOfferAllowedAction } from '@/apiClient/v1/new'
import type { CollectiveOfferStockFormValues } from '@/commons/core/OfferEducational/types'
import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import { generateValidationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const values = {
    startDate: '2050-09-01',
    endDate: '2050-09-02',
    bookingLimitDate: '2050-08-31',
    eventTime: '14:00',
    numberOfTickets: 56,
    educationalPriceDetail: 'Détails sur le prix',
    totalPrice: 1500,
  }

  const cases: {
    description: string
    offerAllowedActions: CollectiveOfferAllowedAction[]
    formValues: Partial<CollectiveOfferStockFormValues>
    expectedErrors: string[]
    isReadOnly?: boolean
    preventPriceIncrease?: boolean
  }[] = [
    {
      description: 'start and end date should be on same school year',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      formValues: {
        ...values,
        endDate: addYears(values.startDate, 2).toISOString().split('T')[0],
      },
      expectedErrors: ['Les dates doivent être sur la même année scolaire'],
    },
    {
      description:
        'should allow a start datetime set on 01/09/N and an end datetime set on 31/08/N+1',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      formValues: {
        ...values,
        startDate: '2050-09-01',
        endDate: '2051-08-31',
      },
      expectedErrors: [],
    },
    {
      description: 'booking datetime should not be after start datetime',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
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
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      formValues: {
        ...values,
        startDate: new Date().toISOString().split('T')[0],
        endDate: addDays(new Date(), 2).toISOString().split('T')[0],
        bookingLimitDate: new Date().toISOString().split('T')[0],
        eventTime: format(subMinutes(new Date(), 1), 'HH:mm'),
      },
      expectedErrors: ["L'heure doit être postérieure à l'heure actuelle"],
    },
    {
      description: 'number of participants should be at least 1',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      formValues: {
        ...values,
        numberOfTickets: 0,
      },
      expectedErrors: ['Minimum 1 participant'],
    },
    {
      description: 'number of participants should not exceed 3000',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      formValues: {
        ...values,
        numberOfTickets: 3001,
      },
      expectedErrors: ['Le nombre de participants ne doit pas dépasser 3000'],
    },
    {
      description: 'price should be at least 0',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      formValues: {
        ...values,
        totalPrice: -1,
      },
      expectedErrors: ['Nombre positif attendu'],
    },
    {
      description: 'price should not exceed 60000',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      formValues: {
        ...values,
        totalPrice: 60001,
      },
      expectedErrors: ['Le prix ne doit pas dépasser 60 000€'],
    },
    {
      description: 'booking limit date should not be in the past',
      offerAllowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
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
      offerAllowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
      formValues: {
        ...values,
        bookingLimitDate: '2024-08-31T13:00:00Z',
      },
      expectedErrors: [],
    },
    {
      description:
        'bookingLimitDate: la règle ne s’applique pas si CAN_EDIT_DATES=false',
      offerAllowedActions: [],
      formValues: {
        ...values,
        bookingLimitDate: '2000-01-01',
      },
      expectedErrors: [],
    },
  ]

  cases.forEach(
    ({ description, offerAllowedActions, formValues, expectedErrors }) => {
      it(`should validate the form for case: ${description}`, async () => {
        const initialPrice = 0
        const errors = await getYupValidationSchemaErrors(
          generateValidationSchema(offerAllowedActions, initialPrice),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    }
  )
})
