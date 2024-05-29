import * as yup from 'yup'

export const validationSchema = yup.object().shape({
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
