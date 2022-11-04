import * as yup from 'yup'

const validationSchema = {
  addressAutocomplete: yup
    .string()
    .required('Veuillez sélectionner une adresse parmi les propositions'),
}

export default validationSchema
