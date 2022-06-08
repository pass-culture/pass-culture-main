import * as yup from 'yup'

const validationSchema = {
  offererId: yup.string().required('Veuillez sélectionner une structure'),
  venueId: yup.string().when('offererId', {
    is: (offererId: string) => offererId !== undefined,
    then: yup.string().required('Veuillez sélectionner un lieu'),
    otherwise: yup.string(),
  }),
}

export default validationSchema
