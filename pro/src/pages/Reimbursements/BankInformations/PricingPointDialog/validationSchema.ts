import * as yup from 'yup'

export const getValidationSchema = yup.object().shape({
  pricingPointId: yup
    .string()
    .required('Veuillez sélectionner une structure avec SIRET'),
})
