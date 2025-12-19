import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'

import { validationSchema } from '../validationSchema'

describe('Activity validationSchema', () => {
  const validFormValues: ActivityFormValues = {
    venueTypeCode: 'MUSEUM',
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
    withCulturalDomains: boolean
  }[] = [
    {
      description: 'complete form',
      formValues: validFormValues,
      expectedErrors: [],
      withCulturalDomains: false,
    },
    {
      description: 'no venue type code',
      formValues: { ...validFormValues, venueTypeCode: '' },
      expectedErrors: ['Veuillez sélectionner une activité principale'],
      withCulturalDomains: false,
    },
    {
      description: 'invalid social url',
      formValues: { ...validFormValues, socialUrls: [{ url: 'abcd' }] },
      expectedErrors: [
        'Veuillez renseigner une URL valide. Ex : https://exemple.com',
      ],
      withCulturalDomains: false,
    },
    {
      description: 'No target customer',
      formValues: {
        ...validFormValues,
        targetCustomer: { individual: false, educational: false },
      },
      expectedErrors: ['Veuillez sélectionner au moins une option'],
      withCulturalDomains: false,
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
      withCulturalDomains: false,
    },
    {
      description: 'No cultural domain but not required',
      formValues: {
        ...validFormValues,
        culturalDomains: [],
      },
      expectedErrors: [],
      withCulturalDomains: false,
    },
    {
      description: 'No cultural domain when required',
      formValues: {
        ...validFormValues,
        culturalDomains: undefined,
      },
      expectedErrors: [
        'Veuillez sélectionner un ou plusieurs domaines d’activité',
      ],
      withCulturalDomains: true,
    },
    {
      description: 'Empty cultural domain when required',
      formValues: {
        ...validFormValues,
        culturalDomains: [],
      },
      expectedErrors: [
        'Veuillez sélectionner un ou plusieurs domaines d’activité',
      ],
      withCulturalDomains: true,
    },
  ]

  cases.forEach(
    ({ description, formValues, expectedErrors, withCulturalDomains }) => {
      it(`should validate the form for case: ${description} ${withCulturalDomains ? 'with' : 'without'} cultural domains`, async () => {
        const errors = await getYupValidationSchemaErrors(
          validationSchema(withCulturalDomains),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    }
  )
})
