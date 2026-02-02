import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'

import { validationSchema } from '../validationSchema'

describe('Activity validationSchema', () => {
  const validFormValues: ActivityFormValues = {
    activity: 'MUSEUM',
    socialUrls: [{ url: 'https://passculture.pro' }],
    targetCustomer: {
      individual: true,
      educational: true,
    },
    phoneNumber: '+33612345678',
    culturalDomains: ['Danse'],
  }

  const cases: {
    description: string
    formValues: ActivityFormValues
    expectedErrors: string[]
    notOpenToPublic: boolean
  }[] = [
    {
      description: 'complete form',
      formValues: validFormValues,
      expectedErrors: [],
      notOpenToPublic: false,
    },
    {
      description: 'no venue type code',
      formValues: { ...validFormValues, activity: undefined },
      expectedErrors: ['Veuillez sélectionner une activité principale'],
      notOpenToPublic: false,
    },
    {
      description: 'invalid social url',
      formValues: { ...validFormValues, socialUrls: [{ url: 'abcd' }] },
      expectedErrors: [
        'Veuillez renseigner une URL valide. Ex : https://exemple.com',
      ],
      notOpenToPublic: false,
    },
    {
      description: 'No target customer',
      formValues: {
        ...validFormValues,
        targetCustomer: { individual: false, educational: false },
      },
      expectedErrors: ['Veuillez sélectionner au moins une option'],
      notOpenToPublic: false,
    },
    {
      description: 'No phone number',
      formValues: {
        ...validFormValues,
        phoneNumber: '',
      },
      expectedErrors: [
        'Veuillez renseigner au moins 10 chiffres',
        'Veuillez renseigner un numéro de téléphone',
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678',
      ],
      notOpenToPublic: false,
    },
    {
      description: 'No cultural domain but not required',
      formValues: {
        ...validFormValues,
        culturalDomains: [],
      },
      expectedErrors: [],
      notOpenToPublic: false,
    },
    {
      description: 'No cultural domain when required',
      formValues: {
        ...validFormValues,
        culturalDomains: undefined,
      },
      expectedErrors: [
        'Activité non valide',
        'Veuillez sélectionner un ou plusieurs domaines d’activité',
      ],
      notOpenToPublic: true,
    },
    {
      description: 'Empty cultural domain when required',
      formValues: {
        ...validFormValues,
        culturalDomains: [],
      },
      expectedErrors: [
        'Activité non valide',
        'Veuillez sélectionner un ou plusieurs domaines d’activité',
      ],
      notOpenToPublic: true,
    },
    {
      description: 'Wrong cultural domain',
      formValues: {
        ...validFormValues,
      },
      expectedErrors: ['Activité non valide'],
      notOpenToPublic: true,
    },
    {
      description: 'Right cultural domain',
      formValues: {
        ...validFormValues,
        activity: 'ART_GALLERY',
      },
      expectedErrors: [],
      notOpenToPublic: false,
    },
    {
      description: 'Right cultural domain',
      formValues: {
        ...validFormValues,
        activity: 'FESTIVAL',
      },
      expectedErrors: [],
      notOpenToPublic: true,
    },
  ]

  cases.forEach(
    ({ description, formValues, expectedErrors, notOpenToPublic }) => {
      it(`should validate the form for case: ${description} ${notOpenToPublic ? 'not ' : ''}open to public`, async () => {
        const errors = await getYupValidationSchemaErrors(
          validationSchema(notOpenToPublic),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    }
  )
})
