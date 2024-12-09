import * as yup from 'yup'

import {
  isPhoneValid,
  passwordValidationStatus,
} from 'commons/core/shared/utils/validation'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .max(120)
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com')
    .required('Veuillez renseigner une adresse email'),
  password: yup
    .string()
    .required('Veuillez renseigner un mot de passe')
    .test(
      'isPasswordValid',
      'Veuillez renseigner un mot de passe valide avec : ',
      (paswordValue) => {
        const errors = passwordValidationStatus(paswordValue)
        const hasError = Object.values(errors).some((error) => error)
        return !hasError
      }
    ),
  lastName: yup.string().max(128).required('Veuillez renseigner votre nom'),
  firstName: yup.string().max(128).required('Veuillez renseigner votre prénom'),
  phoneNumber: yup
    .string()
    .min(10, 'Veuillez renseigner au moins 10 chiffres')
    .max(20, 'Veuillez renseigner moins de 20 chiffres')
    .required('Veuillez renseigner un numéro de téléphone')
    .test(
      'isPhoneValid',
      'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678',
      (phone) => isPhoneValid({ phone, emptyAllowed: false })
    ),
  contactOk: yup.string(),
})
