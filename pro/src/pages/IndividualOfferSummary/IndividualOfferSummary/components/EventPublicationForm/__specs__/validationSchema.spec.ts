import { getYupValidationSchemaErrors } from 'commons/utils/yupValidationTestHelpers'
import { subDays } from 'date-fns'

import { EventPublicationFormValues } from '../types'
import { validationSchema } from '../validationSchema'

describe('EventPublicationForm validationSchema', () => {
  const defaultValues: EventPublicationFormValues = {
    bookingAllowedMode: 'now',
    publicationMode: 'now',
  }

  const cases: {
    description: string
    formValues: EventPublicationFormValues
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form for immediate booking and publication',
      formValues: defaultValues,
      expectedErrors: [],
    },
    {
      description:
        'should have a publication date and time if the publication is scheduled for later',
      formValues: { ...defaultValues, publicationMode: 'later' },
      expectedErrors: [
        'Veuillez sélectionner une date de publication',
        'Veuillez sélectionner une heure de publication',
      ],
    },
    {
      description:
        'should have a booking date and time if the booking availability is scheduled for later',
      formValues: { ...defaultValues, bookingAllowedMode: 'later' },
      expectedErrors: [
        'Veuillez sélectionner une date de réservabilité',
        'Veuillez sélectionner une heure de réservabilité',
      ],
    },
    {
      description: 'should not be able to publish in the past',
      formValues: {
        ...defaultValues,
        publicationMode: 'later',
        publicationDate: subDays(new Date(), 1).toISOString().split('T')[0],
        publicationTime: '01:01',
      },
      expectedErrors: ['Veuillez indiquer une date dans le futur'],
    },
    {
      description: 'should not be able to publish earlier today',
      formValues: {
        ...defaultValues,
        publicationMode: 'later',
        publicationDate: new Date().toISOString().split('T')[0],
        publicationTime: '00:00',
      },
      expectedErrors: ['Veuillez indiquer une heure dans le futur'],
    },
    {
      description: 'should not be able to make an offer bookable in the past',
      formValues: {
        ...defaultValues,
        bookingAllowedMode: 'later',
        bookingAllowedDate: subDays(new Date(), 1).toISOString().split('T')[0],
        bookingAllowedTime: '01:01',
      },
      expectedErrors: ['Veuillez indiquer une date dans le futur'],
    },
    {
      description: 'should not be able to make an offer bookable earlier today',
      formValues: {
        ...defaultValues,
        bookingAllowedMode: 'later',
        bookingAllowedDate: new Date().toISOString().split('T')[0],
        bookingAllowedTime: '00:00',
      },
      expectedErrors: ['Veuillez indiquer une heure dans le futur'],
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
