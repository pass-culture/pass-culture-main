import * as yup from 'yup'

const validationSchema = {
  venueType: yup
    .string()
    .required('Veuillez sélectionner une activité principale'),
}

export default validationSchema
