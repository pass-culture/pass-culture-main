import * as yup from 'yup'

import { isPhoneValid } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { emailSchema } from 'commons/utils/isValidEmail'
import { passwordValidationStatus } from 'ui-kit/form/PasswordInput/validation'

export const validationSchema = (isNewSignupEnabled: boolean) => {
  const schemaObject = {
    email: yup
      .string()
      .required('Veuillez renseigner une adresse email')
      .test(emailSchema),
    password: yup
      .string()
      .required()
      .test('isPasswordValid', (passwordValue) => {
        const errors = passwordValidationStatus(passwordValue)
        const hasError = Object.values(errors).some((error) => error)
        return !hasError
      }),
    lastName: yup.string().max(128).required('Veuillez renseigner votre nom'),
    firstName: yup
      .string()
      .max(128)
      .required('Veuillez renseigner votre prénom'),
    contactOk: yup.boolean().default(false), // optional field, but defaults to "false"
    token: yup.string().default(''), // this allows to pass hookForm validation and set the token after form submission
  }

  // if the FF WIP_2025_SIGN_UP is enabled, the field "phoneNumber" is no longer in the SignUp
  if (isNewSignupEnabled) {
    return yup.object().shape(schemaObject)
  }
  // else, field "phoneNumber" is part of SignUp, so we include it in the schema
  else {
    return yup.object().shape({
      ...schemaObject,

      // Adds "phoneNumber" validation
      phoneNumber: yup
        .string()
        .required('Veuillez renseigner un numéro de téléphone')
        .test(
          'isPhoneValid',
          'Veuillez renseigner un numéro de téléphone valide',
          isPhoneValid
        ),
    })
  }
}
