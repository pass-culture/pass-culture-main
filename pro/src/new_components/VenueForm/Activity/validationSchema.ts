import * as yup from 'yup'

const validationSchema = {
  venueType: yup.string().required('Veuillez sélectionner un type de lieu'),
}

export default validationSchema
