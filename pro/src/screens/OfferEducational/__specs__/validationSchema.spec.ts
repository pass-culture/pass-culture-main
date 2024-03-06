import { EacFormat, OfferAddressType, StudentLevels } from 'apiClient/v1'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

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
    all: false,
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
  formats: [EacFormat.CONCERT],
  contactOptions: {
    email: true,
    form: false,
    phone: false,
  },
  interventionArea: ['45'],
}

describe('validationSchema OfferEducational', () => {
  describe('template offer', () => {
    const cases: {
      description: string
      formValues: Partial<OfferEducationalFormValues>
      expectedErrors: string[]
      isCustomContactActive: boolean
    }[] = [
      {
        description: 'valid form',
        formValues: defaultValues,
        expectedErrors: [],
        isCustomContactActive: true,
      },
      {
        description: 'not valid form without any contact option and FF active',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: false, phone: false },
        },
        expectedErrors: ['Veuillez sélectionner au moins un moyen de contact'],
        isCustomContactActive: true,
      },
      {
        description:
          'not valid form with email option checked but field empty and FF active',
        formValues: {
          ...defaultValues,
          contactOptions: { email: true, form: false, phone: false },
          email: '',
        },
        expectedErrors: ['Veuillez renseigner une adresse email'],
        isCustomContactActive: true,
      },
      {
        description: 'not valid form with email field empty and FF inactive',
        formValues: {
          ...defaultValues,
          contactOptions: undefined,
          email: '',
        },
        expectedErrors: ['Veuillez renseigner une adresse email'],
        isCustomContactActive: false,
      },
      {
        description: 'not valid form with email field invalid and FF inactive',
        formValues: {
          ...defaultValues,
          contactOptions: undefined,
          email: 'invalidEmailString',
        },
        expectedErrors: [
          'Veuillez renseigner une adresse email valide, exemple : mail@exemple.com',
        ],
        isCustomContactActive: false,
      },
      {
        description:
          'not valid form with phone option checked but field empty and FF active',
        formValues: {
          ...defaultValues,
          contactOptions: { email: true, form: false, phone: true },
          phone: '',
        },
        expectedErrors: ['Veuillez renseigner un numéro de téléphone'],
        isCustomContactActive: true,
      },
      {
        description: 'valid form with phone field empty and FF inactive',
        formValues: {
          ...defaultValues,
          contactOptions: undefined,
          phone: '',
        },
        expectedErrors: [],
        isCustomContactActive: false,
      },
      {
        description:
          'valid form with form option checked and default form selected and FF active',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'form',
        },
        expectedErrors: [],
        isCustomContactActive: true,
      },
      {
        description:
          'invalid form with form option checked and url form selected but custom url field empty and FF active',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'url',
          contactUrl: '',
        },
        expectedErrors: ['Veuillez renseigner une URL de contact'],
        isCustomContactActive: true,
      },
      {
        description:
          'invalid form with form option checked and url form selected but custom url invalid and FF active',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'url',
          contactUrl: 'testInvalidUrl',
        },
        expectedErrors: [
          'Veuillez renseigner une URL valide, exemple : https://mon-formulaire.fr',
        ],
        isCustomContactActive: true,
      },
      {
        description:
          'valid form with form option checked and url form selected and custom url valid and FF active',
        formValues: {
          ...defaultValues,
          contactOptions: { email: false, form: true, phone: false },
          contactFormType: 'url',
          contactUrl: 'http://testValidUrl.com',
        },
        expectedErrors: [],
        isCustomContactActive: true,
      },
    ]

    cases.forEach(
      ({ description, formValues, expectedErrors, isCustomContactActive }) => {
        it(`should validate the form for case: ${description}`, async () => {
          const errors = await getYupValidationSchemaErrors(
            getOfferEducationalValidationSchema(isCustomContactActive),
            formValues
          )
          expect(errors).toEqual(expectedErrors)
        })
      }
    )
  })
})
