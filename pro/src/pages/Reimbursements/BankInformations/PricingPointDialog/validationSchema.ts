import * as yup from 'yup'

const validationSchema = () =>
  yup.object().shape({
    pricingPointId: yup
      .string()
      .required('Veuillez sélectionner un lieu avec SIRET'),
  })

export default validationSchema
