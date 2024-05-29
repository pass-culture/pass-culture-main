import * as yup from 'yup'

export const validationSchema = () =>
  yup.object().shape({
    pricingPointId: yup
      .string()
      .required('Veuillez sélectionner un lieu avec SIRET'),
  })
