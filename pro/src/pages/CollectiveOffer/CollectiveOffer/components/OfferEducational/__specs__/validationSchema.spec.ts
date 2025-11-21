import {
  CollectiveLocationType,
  EacFormat,
  StudentLevels,
} from '@/apiClient/v1'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import { getOfferEducationalValidationSchema } from '../validationSchema'

const defaultValues: OfferEducationalFormValues = {
  title: 'offer title',
  email: 'test@test.co',
  notificationEmails: [{ email: 'test@test.co' }],
  accessibility: {
    audio: false,
    mental: false,
    motor: false,
    visual: false,
    none: true,
  },
  description: 'Lorem ipsum',
  domains: ['Domain 1'],
  isTemplate: true,
  participants: Object.fromEntries(
    Object.keys(StudentLevels).map((level) => [level, true])
  ) as Record<StudentLevels, boolean>,
  phone: '',
  offererId: '123',
  venueId: '1234',
  duration: '10:10',
  location: {
    locationType: CollectiveLocationType.ADDRESS,
    location: {
      id: undefined,
      isManualEdition: false,
      isVenueLocation: false,
      label: '',
    },
  },
  formats: [EacFormat.CONCERT],
  contactOptions: {
    email: true,
    form: false,
    phone: false,
  },
  interventionArea: ['45'],
  'search-addressAutocomplete': '',
  addressAutocomplete: '',
}

describe('validationSchema OfferEducational', () => {
  describe('template offer', () => {
    const cases: {
      description: string
      formValues: Partial<OfferEducationalFormValues>
      expectedErrors: string[]
    }[] = [
      {
        description: 'valid form',
        formValues: defaultValues,
        expectedErrors: [],
      },
      {
        description: 'not valid form without any contact option',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: false, phone: false },
        },
        expectedErrors: ['Veuillez sélectionner au moins un moyen de contact'],
      },
      {
        description: 'not valid form with email option checked but field empty',
        formValues: {
          ...defaultValues,
          contactOptions: { email: true, form: false, phone: false },
          email: '',
        },
        expectedErrors: ['Veuillez renseigner une adresse email'],
      },
      {
        description: 'not valid form with phone option checked but field empty',
        formValues: {
          ...defaultValues,
          contactOptions: { email: true, form: false, phone: true },
          phone: '',
        },
        expectedErrors: ['Veuillez renseigner un numéro de téléphone'],
      },
      {
        description:
          'valid form with form option checked and default form selected',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'form',
        },
        expectedErrors: [],
      },
      {
        description:
          'invalid form with form option checked and url form selected but custom url field empty',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'url',
          contactUrl: '',
        },
        expectedErrors: ['Veuillez renseigner une URL de contact'],
      },
      {
        description:
          'invalid form with form option checked and url form selected but custom url invalid',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'url',
          contactUrl: 'testInvalidUrl',
        },
        expectedErrors: [
          'Veuillez renseigner une URL valide, exemple : https://mon-formulaire.fr',
        ],
      },
      {
        description:
          'valid form with form option checked and url form selected and custom url valid',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'url',
          contactUrl: 'http://testValidUrl.com',
        },
        expectedErrors: [],
      },
      {
        description: 'valid form without notification email',
        formValues: {
          ...defaultValues,
          notificationEmails: [{ email: '' }],
        },
        expectedErrors: ['Veuillez renseigner une adresse email'],
      },
      {
        description:
          'invalid form with specific address without address selectio',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            location: {
              id: 'SPECIFIC_ADDRESS',
              isManualEdition: false,
              isVenueLocation: false,
              label: '',
            },
          },
          addressAutocomplete: '',
        },
        expectedErrors: [
          'Veuillez sélectionner une adresse parmi les suggestions',
        ],
      },
      {
        description:
          'invalid form with specific address without manual address fields',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            location: {
              id: 'SPECIFIC_ADDRESS',
              isManualEdition: true,
              isVenueLocation: false,
              label: '',
            },
          },
        },
        expectedErrors: [
          'Veuillez renseigner une adresse postale',
          'Veuillez renseigner un code postal',
          'Veuillez renseigner une ville',
          'Veuillez renseigner les coordonnées GPS',
        ],
      },
      {
        description:
          'invalid form with wrong gps coordinates in manual address',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            location: {
              id: 'SPECIFIC_ADDRESS',
              isManualEdition: true,
              isVenueLocation: false,
              label: '',
            },
          },
          street: '1 rue du chemin',
          city: 'Brest',
          postalCode: '29000',
          coords: 'blabla',
        },
        expectedErrors: ['Veuillez respecter le format attendu'],
      },
      {
        description:
          'invalid form when school location is selected without departments',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.SCHOOL,
          },
          interventionArea: [],
        },
        expectedErrors: ['Veuillez renseigner au moins un département'],
      },
      {
        description:
          'invalid form when to_be_defined location is selected without departments',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.TO_BE_DEFINED,
          },
          interventionArea: [],
        },
        expectedErrors: ['Veuillez renseigner au moins un département'],
      },
      {
        description: 'valid when duration is greater than 23:59',
        formValues: {
          ...defaultValues,
          duration: '70:00',
        },
        expectedErrors: [],
      },
      {
        description:
          'valid form when postalCode is not required and if locationType is not ADDRESS',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.SCHOOL,
            location: {
              isManualEdition: false,
            },
          },
          postalCode: '',
          interventionArea: ['45'],
        },
        expectedErrors: [],
      },
      {
        description:
          'invalid form when postalCode is required and postalCode is not 5 chars',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            location: {
              id: 'SPECIFIC_ADDRESS',
              isManualEdition: true,
            },
          },
          street: '1 rue du chemin',
          city: 'Brest',
          postalCode: '123',
          coords: '48.853320, 2.348979',
        },
        expectedErrors: ['Veuillez renseigner un code postal valide'],
      },
    ]

    cases.forEach(({ description, formValues, expectedErrors }) => {
      it(`should validate the form for case: ${description}`, async () => {
        const errors = await getYupValidationSchemaErrors(
          getOfferEducationalValidationSchema(),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    })
  })
})
