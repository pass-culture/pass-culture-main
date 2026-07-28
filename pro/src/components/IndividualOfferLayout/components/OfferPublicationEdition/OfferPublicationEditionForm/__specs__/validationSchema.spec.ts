import { subDays } from 'date-fns'

import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import type { EventPublicationEditionFormValues } from '../types'
import { validationSchema } from '../validationSchema'

describe('OfferPublicationEditionForm validationSchema', () => {
  const defaultValues: EventPublicationEditionFormValues = {
    isPaused: false,
    publicationMode: 'now',
    bookingAllowedMode: 'now',
  }

  const cases: {
    description: string
    formValues: EventPublicationEditionFormValues
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form for publication and booking allowed date now',
      formValues: defaultValues,
      expectedErrors: [],
    },
    {
      description: 'valid form for paused offer',
      formValues: { ...defaultValues, isPaused: true },
      expectedErrors: [],
    },
    {
      description:
        'invalid form for offer bookable later with missing date and time',
      formValues: { ...defaultValues, bookingAllowedMode: 'later' },
      expectedErrors: [
        'Veuillez sélectionner une date de réservabilité',
        'Veuillez sélectionner une heure de réservabilité',
      ],
    },
    {
      description:
        'invalid form for offer bookable later with date in the past',
      formValues: {
        ...defaultValues,
        bookingAllowedMode: 'later',
        bookingAllowedDate: subDays(new Date(), 1).toISOString().split('T')[0],
        bookingAllowedTime: '12:12',
      },
      expectedErrors: ['Veuillez indiquer une date dans le futur'],
    },
    {
      description:
        'invalid form for offer publied later with missing date and time',
      formValues: { ...defaultValues, publicationMode: 'later' },
      expectedErrors: [
        'Veuillez sélectionner une date de publication',
        'Veuillez sélectionner une heure de publication',
      ],
    },
    {
      description: 'invalid form for offer publied later with date in the past',
      formValues: {
        ...defaultValues,
        publicationMode: 'later',
        publicationDate: subDays(new Date(), 1).toISOString().split('T')[0],
        publicationTime: '12:12',
      },
      expectedErrors: ['Veuillez indiquer une date dans le futur'],
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

  it('should pass when publication date is on first booking limit date from context', async () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowDate = tomorrow.toISOString().split('T')[0]

    const formValues: EventPublicationEditionFormValues = {
      ...defaultValues,
      publicationMode: 'later',
      publicationDate: tomorrowDate,
      publicationTime: '12:00',
    }

    const errors = await getYupValidationSchemaErrors(
      validationSchema,
      formValues,
      {
        context: {
          firstBookingLimitDatetime: `${tomorrowDate}T00:00:00.000Z`,
        },
      }
    )

    expect(errors).not.toContain(
      'Veuillez indiquer une date avant la date limite de réservation'
    )
  })

  it('should pass when booking allowed date is on first booking limit date from context', async () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowDate = tomorrow.toISOString().split('T')[0]

    const formValues: EventPublicationEditionFormValues = {
      ...defaultValues,
      bookingAllowedMode: 'later',
      bookingAllowedDate: tomorrowDate,
      bookingAllowedTime: '12:00',
    }

    const errors = await getYupValidationSchemaErrors(
      validationSchema,
      formValues,
      {
        context: {
          firstBookingLimitDatetime: `${tomorrowDate}T00:00:00.000Z`,
        },
      }
    )

    expect(errors).not.toContain(
      'Veuillez indiquer une date avant la date limite de réservation'
    )
  })
})
