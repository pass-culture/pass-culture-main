import * as yup from 'yup'

export const validationSchema = {
  offererId: yup.string().required('Veuillez sélectionner une structure'),
  venueId: yup.string().when('offererId', {
    is: (offererId: string) => offererId,
    then: (schema) => schema.required('Veuillez sélectionner un lieu'),
  }),
}
