import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  publicationDate: yup.string().when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema.required('Veuillez sélectionner une date de publication'),
  }),
  publicationTime: yup.string().when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema.required('Veuillez sélectionner une heure de publication'),
  }),
})
