import * as yup from 'yup'

export const validationSchema = {
  addressAutocomplete: yup
    .string()
    .required('Veuillez sélectionner une adresse parmi les suggestions'),
}
