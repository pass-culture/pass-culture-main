import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .max(120)
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com')
    .required('Veuillez renseigner votre nouvel email'),
  password: yup
    .string()
    .max(128)
    .required('Veuillez renseigner votre mot de passe'),
})
