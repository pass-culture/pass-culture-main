import type { ProUserCreationBodyV2Model } from '@/apiClient/v1'
import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import { validationSchema } from '../validationSchema'

const signupFormDefault = {
  email: 'email@gmail.com',
  password: 'P@ssW0rD123123', // NOSONAR
  firstName: 'first name',
  lastName: 'last name',
  contactOk: true,
}

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: Partial<ProUserCreationBodyV2Model>
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
      description: 'not valid form without password',
      formValues: { ...signupFormDefault, password: '' },
      expectedErrors: ['Veuillez renseigner un mot de passe'], // default yup message
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
