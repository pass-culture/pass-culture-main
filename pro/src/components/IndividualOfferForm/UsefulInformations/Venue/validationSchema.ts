import * as yup from 'yup'

const validationSchema = {
  offererId: yup.string().required('Veuillez sélectionner une structure'),
  venueId: yup.string().when('offererId', {
    is: (offererId: string) => offererId !== undefined,
    then: schema => schema.required('Veuillez sélectionner un lieu'),
  }),
}

export default validationSchema
