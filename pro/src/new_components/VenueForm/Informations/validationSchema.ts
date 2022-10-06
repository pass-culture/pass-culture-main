import * as yup from 'yup'

const validationSchema = {
  mail: yup
    .string()
    .required('Veuillez renseigner une adresse e-mail')
    .email('Veuillez renseigner un e-mail valide'),
  name: yup.string().required('Veuillez renseigner un nom'),
  venueType: yup.string().required('Veuillez sélectionner un type de lieu'),
}

export default validationSchema
