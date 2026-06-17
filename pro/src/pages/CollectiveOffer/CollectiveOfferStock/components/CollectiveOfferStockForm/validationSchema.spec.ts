import { addDays, addYears, format, subMinutes } from 'date-fns'

import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

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
  }

  it.each([
    {
      description: 'should require mandatory fields',
      canEditDates: true,
      formValues: {},
      expectedErrors: [
        'La date de début est obligatoire',
        'La date de fin est obligatoire',
        'L’horaire est obligatoire',
        "Le nombre d'élèves est obligatoire",
        "Le nombre d'accompagnateurs est obligatoire",
        'La date limite de réservation est obligatoire',
      ],
    },
    {
      description: 'start and end date should be on same school year',
      canEditDates: true,
      formValues: {
        ...values,
        endDate: addYears(values.startDate, 2).toISOString().split('T')[0],
      },
      expectedErrors: ['Les dates doivent être sur la même année scolaire'],
    },
    {
      description:
        'should allow a start datetime set on 01/09/N and an end datetime set on 31/08/N+1',
      canEditDates: true,
      formValues: {
        ...values,
        startDate: '2050-09-01',
        endDate: '2051-08-31',
      },
      expectedErrors: [],
    },
    {
      description: 'booking datetime should not be after start datetime',
      canEditDates: true,
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
      canEditDates: true,
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
      canEditDates: true,
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
      canEditDates: false,
      formValues: {
        ...values,
        bookingLimitDate: '2024-08-31T13:00:00Z',
      },
      expectedErrors: [],
    },
    {
      description:
        'bookingLimitDate: la règle ne s’applique pas si CAN_EDIT_DATES=false',
      canEditDates: false,
      formValues: {
        ...values,
        bookingLimitDate: '2000-01-01',
      },
      expectedErrors: [],
    },
    {
      description: 'number of participants should be at least 1',
      canEditDates: true,
      formValues: {
        ...values,
        numberOfTickets: 0,
      },
      expectedErrors: ['Minimum 1 élève'],
    },
    {
      description: 'number of participants should not exceed 3000',
      canEditDates: true,
      formValues: {
        ...values,
        numberOfTickets: 3001,
      },
      expectedErrors: ["Le nombre d'élèves ne doit pas dépasser 3000"],
    },
    {
      description: 'number of teachers should be at least 0',
      canEditDates: true,
      formValues: {
        ...values,
        numberOfTeachers: -1,
      },
      expectedErrors: ['Minimum 0 accompagnateur'],
    },
    {
      description: 'number of teachers should not exceed 50',
      canEditDates: true,
      formValues: {
        ...values,
        numberOfTeachers: 51,
      },
      expectedErrors: ["Le nombre d'accompagnateurs ne doit pas dépasser 50"],
    },
  ])(`$description`, async ({
    canEditDates,
    formValues,
    expectedErrors,
  }: {
    description: string
    canEditDates: boolean
    formValues: Partial<CollectiveOfferStockFormValues>
    expectedErrors: string[]
  }) => {
    const errors = await getYupValidationSchemaErrors(
      generateValidationSchema(canEditDates),
      formValues
    )
    expect(errors).toEqual(expectedErrors)
  })
})
