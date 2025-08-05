import { emailSchema } from 'commons/utils/isValidEmail'
import { passwordValidationStatus } from 'ui-kit/form/PasswordInput/validation'
import * as yup from 'yup'

export const validationSchema = yup.object().shape({
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
  firstName: yup.string().max(128).required('Veuillez renseigner votre prénom'),
  contactOk: yup.boolean().default(false), // optional field, but defaults to "false"
  token: yup.string().default(''), // this allows to pass hookForm validation and set the token after form submission
})
