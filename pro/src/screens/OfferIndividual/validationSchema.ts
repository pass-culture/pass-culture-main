import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  title: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string().max(1000),
  venueId: yup.string().required('Veuillez sélectionner un lieu'),
})
