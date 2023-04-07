import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  siret: yup.string().required(),
  name: yup.string().required(),
  publicName: yup.string().nullable(),
  addressAutocomplete: yup
    .string()
    .required('Veuillez sélectionner une adresse parmi les suggestions'),
})
