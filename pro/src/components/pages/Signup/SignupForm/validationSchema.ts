import parsePhoneNumberFromString from 'libphonenumber-js'
import * as yup from 'yup'

const passwordErrorMessage = `Votre mot de passe doit contenir au moins :
      - 12 caractères
      - Un chiffre
      - Une majuscule et une minuscule
      - Un caractère spécial
`

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .max(120)
    .email('Veuillez renseigner un email valide')
    .required('Veuillez renseigner un email'),
  password: yup
    .string()
    .required('Veuillez renseigner un mot de passe')
    .min(12, passwordErrorMessage)
    .test('isPasswordValid', passwordErrorMessage, value => {
      if (!value) return false
      const hasUpperCase = /[A-Z]/.test(value)
      const hasLowerCase = /[a-z]/.test(value)
      const hasNumber = /[0-9]/.test(value)
      const hasSymbole = /[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(value)
      if (hasUpperCase && hasLowerCase && hasNumber && hasSymbole) {
        return true
      }
      return false
    }),
  lastName: yup.string().max(128).required('Veuillez renseigner votre nom'),
  firstName: yup.string().max(128).required('Veuillez renseigner votre prénom'),
  // TODO (mageoffray, 2022-05-12): Create a generic validator method for phone validation
  phoneNumber: yup
    .string()
    .min(10, 'Veuillez renseigner au moins 10 chiffres')
    .max(20, 'Veuillez renseigner moins de 20 chiffres')
    .required('Veuillez renseigner votre numéro de téléphone')
    .test(
      'isPhoneValid',
      'Votre numéro de téléphone n’est pas valide',
      value => {
        if (!value) return false
        const phoneNumber = parsePhoneNumberFromString(value, 'FR')
        const isValid = phoneNumber?.isValid()
        if (!isValid) return false
        return true
      }
    ),
  contactOk: yup.string(),
  siren: yup
    .string()
    .required('Veuillez rensigner le siren de votre entreprise')
    .min(9, 'Veuillez saisir 9 chiffres')
    .max(11, 'Veuillez saisir 9 chiffres'),
})
