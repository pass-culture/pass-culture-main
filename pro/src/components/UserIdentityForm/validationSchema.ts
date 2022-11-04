import * as yup from 'yup'

const validationSchema = yup.object().shape({
  firstName: yup
    .string()
    .max(128, 'Veuillez renseigner moins de 128 caractères')
    .trim()
    .required('Veuillez renseigner votre prénom'),
  lastName: yup
    .string()
    .max(128, 'Veuillez renseigner moins de 128 caractères')
    .trim()
    .required('Veuillez renseigner votre nom'),
})

export default validationSchema
