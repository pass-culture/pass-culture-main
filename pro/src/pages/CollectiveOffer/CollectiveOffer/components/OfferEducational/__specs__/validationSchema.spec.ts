import {
  CollectiveLocationType,
  EacFormat,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { getYupValidationSchemaErrors } from 'commons/utils/yupValidationTestHelpers'

import { getOfferEducationalValidationSchema } from '../validationSchema'

const defaultValues: OfferEducationalFormValues = {
  title: 'offer title',
  email: 'test@test.co',
  notificationEmails: ['test@test.co'],
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
  participants: {
    ...(Object.fromEntries(
      Object.keys(StudentLevels).map((level) => [level, true])
    ) as Record<StudentLevels, boolean>),
    college: false,
    lycee: false,
    marseille: false,
  },
  phone: '',
  offererId: '123',
  venueId: '1234',
  duration: '10:10',
  eventAddress: {
    addressType: OfferAddressType.OTHER,
    otherAddress: '123 address',
    venueId: 1234,
  },
  location: {
    locationType: CollectiveLocationType.ADDRESS,
    address: {
      id_oa: undefined,
      isManualEdition: false,
      isVenueAddress: false,
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
      isCollectiveOaActive?: boolean
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
          notificationEmails: [''],
        },
        expectedErrors: ['Veuillez renseigner une adresse email'],
      },
      {
        description:
          'invalid form with specific address without address selection when OA FF is active',
        formValues: {
          ...defaultValues,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            address: {
              id_oa: 'SPECIFIC_ADDRESS',
              isManualEdition: false,
              isVenueAddress: false,
              label: '',
            },
          },
          addressAutocomplete: '',
        },
        expectedErrors: [
          'Veuillez sélectionner une adresse parmi les suggestions',
        ],
        isCollectiveOaActive: true,
      },
    ]

    cases.forEach(
      ({
        description,
        formValues,
        expectedErrors,
        isCollectiveOaActive = false,
      }) => {
        it(`should validate the form for case: ${description}`, async () => {
          const errors = await getYupValidationSchemaErrors(
            getOfferEducationalValidationSchema(isCollectiveOaActive),
            formValues
          )
          expect(errors).toEqual(expectedErrors)
        })
      }
    )
  })
})
