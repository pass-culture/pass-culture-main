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
      description: 'valid form without SIREN',
      formValues: signupFormDefault,
      expectedErrors: [],
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
