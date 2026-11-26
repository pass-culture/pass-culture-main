import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'
import type { OffererAuthenticationFormValues } from '@/components/SignupJourneyForm/Authentication/OffererAuthenticationForm'

import { validationSchema } from '../validationSchema'

describe('OffererAuthenticationForm validationSchema', () => {
  const defaultValues = {
    siret: '12345678901235',
    name: 'name',
    publicName: 'name',
    addressAutocomplete: 'adress',
    'search-addressAutocomplete': 'address',
    coords: '123,123',
    manuallySetAddress: false,
    isOpenToPublic: 'true',
    city: 'city',
    latitude: 1,
    longitude: 1,
    postalCode: '93150',
    street: 'street',
    banId: 'ban',
    inseeCode: 'insee',
  }
  const cases: {
    description: string
    formValues: OffererAuthenticationFormValues
    expectedErrors: string[]
    notDiffusible: boolean
  }[] = [
    {
      description: 'valid form for diffusible siret',
      formValues: defaultValues,
      expectedErrors: [],
      notDiffusible: false,
    },
    {
      description: 'valid form for not diffusible siret',
      formValues: defaultValues,
      expectedErrors: [],
      notDiffusible: true,
    },
    {
      description: 'invalid form without siret',
      formValues: { ...defaultValues, siret: '' },
      expectedErrors: ['siret is a required field'],
      notDiffusible: false,
    },
    {
      description: 'invalid form without name for diffusible siret',
      formValues: { ...defaultValues, name: '' },
      expectedErrors: ['name is a required field'],
      notDiffusible: false,
    },
    {
      description: 'valid form without name for not diffusible siret',
      formValues: { ...defaultValues, name: '' },
      expectedErrors: [],
      notDiffusible: true,
    },
    {
      description: 'invalid form without public name for not diffusible siret',
      formValues: { ...defaultValues, publicName: '' },
      expectedErrors: [
        'Veuillez renseigner un nom public pour votre structure',
      ],
      notDiffusible: true,
    },
    {
      description: 'valid form without publicname for  diffusible siret',
      formValues: { ...defaultValues, publicName: '' },
      expectedErrors: [],
      notDiffusible: false,
    },
    {
      description: 'invalid form without isOpenToPublic',
      formValues: { ...defaultValues, isOpenToPublic: '' },
      expectedErrors: ['Veuillez sélectionner une option'],
      notDiffusible: false,
    },
    {
      description: 'invalid form without a street',
      formValues: { ...defaultValues, street: '' },
      expectedErrors: ['Veuillez renseigner une adresse postale'],
      notDiffusible: false,
    },
    {
      description:
        'invalid non-diffusible street for a venue open to the public',
      formValues: {
        ...defaultValues,
        isOpenToPublic: 'true',
        street: 'Adresse non diffusée',
      },
      expectedErrors: [
        'Pour accueillir du public, veuillez renseigner une adresse précise',
      ],
      notDiffusible: true,
    },
    {
      description:
        'valid non-diffusible street for a venue closed to the public',
      formValues: {
        ...defaultValues,
        isOpenToPublic: 'false',
        street: 'Adresse non diffusée',
      },
      expectedErrors: [],
      notDiffusible: true,
    },
  ]

  cases.forEach(
    ({ description, formValues, expectedErrors, notDiffusible }) => {
      it(`should validate the form for case: ${description}`, async () => {
        const errors = await getYupValidationSchemaErrors(
          validationSchema(notDiffusible),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    }
  )
})
