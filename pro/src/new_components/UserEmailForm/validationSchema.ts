import * as yup from 'yup'

const validationSchema = yup.object().shape({
  email: yup
    .string()
    .max(120)
    .email('Veuillez renseigner un adresse e-mail valide')
    .required('Veuillez renseigner votre nouvel email'),
  password: yup
    .string()
    .max(128)
    .required('Veuillez renseigner votre mot de passe'),
})

export default validationSchema
