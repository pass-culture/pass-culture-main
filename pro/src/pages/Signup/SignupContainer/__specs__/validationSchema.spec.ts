import { ISignupFormValues } from 'pages/Signup/SignupContainer/types'
import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { validationSchema } from '../validationSchema'

const signupFormDefault = {
  email: 'email@gmail.com',
  password: 'P@ssW0rD123123', // NOSONAR
  firstName: 'first name',
  lastName: 'last name',
  phoneNumber: '0606060606',
  contactOk: true,
}

const signupFormWithSiren = {
  ...signupFormDefault,
  siren: '123123123',
  legalUnitValues: {
    address: 'adress',
    city: 'city',
    name: 'name',
    postalCode: '123123',
    siren: '123123123',
  },
}

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: Partial<ISignupFormValues>
    expectedErrors: string[]
    withoutSiren: boolean
  }[] = [
    {
      description: 'valid form with SIREN',
      formValues: signupFormWithSiren,
      expectedErrors: [],
      withoutSiren: false,
    },
    {
      description: 'valid form with too short SIREN',
      formValues: { ...signupFormWithSiren, siren: '123' },
      expectedErrors: ['Le SIREN doit comporter 9 caractères.'],
      withoutSiren: false,
    },
    {
      description: 'valid form with too long SIREN',
      formValues: { ...signupFormWithSiren, siren: '123456789101112' },
      expectedErrors: ['Le SIREN doit comporter 9 caractères.'],
      withoutSiren: false,
    },
    {
      description: 'valid form without SIREN',
      formValues: signupFormDefault,
      expectedErrors: [],
      withoutSiren: true,
    },
    {
      description: 'not valid form without firstName',
      formValues: { ...signupFormDefault, firstName: '' },
      expectedErrors: ['Veuillez renseigner votre prénom'],
      withoutSiren: true,
    },
    {
      description: 'not valid form without name',
      formValues: { ...signupFormDefault, lastName: '' },
      expectedErrors: ['Veuillez renseigner votre nom'],
      withoutSiren: true,
    },
    {
      description: 'not valid form without phone',
      formValues: { ...signupFormDefault, phoneNumber: '' },
      expectedErrors: [
        'Veuillez renseigner au moins 10 chiffres',
        'Veuillez renseigner un numéro de téléphone',
        'Veuillez renseigner un numéro de téléphone valide',
      ],
      withoutSiren: true,
    },
    {
      description: 'not valid form with too short phone',
      formValues: { ...signupFormDefault, phoneNumber: '0102' },
      expectedErrors: [
        'Veuillez renseigner au moins 10 chiffres',
        'Veuillez renseigner un numéro de téléphone valide',
      ],
      withoutSiren: true,
    },
    {
      description: 'not valid form with invalid and too long phone',
      formValues: {
        ...signupFormDefault,
        phoneNumber: '1234567891011121314151617',
      },
      expectedErrors: [
        'Veuillez renseigner moins de 20 chiffres',
        'Veuillez renseigner un numéro de téléphone valide',
      ],
      withoutSiren: true,
    },
    {
      description: 'not valid form without password',
      formValues: { ...signupFormDefault, password: '' },
      expectedErrors: ['Veuillez renseigner un mot de passe'],
      withoutSiren: true,
    },
    {
      description: 'not valid form with wrong password',
      formValues: { ...signupFormDefault, password: 'aaaaaaaa' },
      expectedErrors: ['Veuillez renseigner un mot de passe valide avec : '],
      withoutSiren: true,
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors, withoutSiren }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        validationSchema(withoutSiren),
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})
