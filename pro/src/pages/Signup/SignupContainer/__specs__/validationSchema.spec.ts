import { SignupFormValues } from 'pages/Signup/SignupContainer/types'
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

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: Partial<SignupFormValues>
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form',
      formValues: signupFormDefault,
      expectedErrors: [],
    },
    {
      description: 'not valid form without firstName',
      formValues: { ...signupFormDefault, firstName: '' },
      expectedErrors: ['Veuillez renseigner votre prénom'],
    },
    {
      description: 'not valid form without name',
      formValues: { ...signupFormDefault, lastName: '' },
      expectedErrors: ['Veuillez renseigner votre nom'],
    },
    {
      description: 'not valid form without phone',
      formValues: { ...signupFormDefault, phoneNumber: '' },
      expectedErrors: [
        'Veuillez renseigner au moins 10 chiffres',
        'Veuillez renseigner un numéro de téléphone',
        'Veuillez renseigner un numéro de téléphone valide',
      ],
    },
    {
      description: 'not valid form with too short phone',
      formValues: { ...signupFormDefault, phoneNumber: '0102' },
      expectedErrors: [
        'Veuillez renseigner au moins 10 chiffres',
        'Veuillez renseigner un numéro de téléphone valide',
      ],
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
    },
    {
      description: 'not valid form without password',
      formValues: { ...signupFormDefault, password: '' },
      expectedErrors: ['Veuillez renseigner un mot de passe'],
    },
    {
      description: 'not valid form with wrong password',
      formValues: { ...signupFormDefault, password: 'aaaaaaaa' }, // NOSONAR
      expectedErrors: ['Veuillez renseigner un mot de passe valide avec : '],
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
