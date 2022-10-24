import * as yup from 'yup'

const validationSchema = {
  name: yup.string().required('Veuillez renseigner un nom'),
  venueType: yup.string().required('Veuillez sélectionner un type de lieu'),
}

export default validationSchema
