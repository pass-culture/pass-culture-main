import * as yup from 'yup'

const validationSchema = yup.object().shape({
  visibility: yup.string().oneOf(['one', 'all']),
  institution: yup.string().when('visibility', {
    is: (visibility: string) => visibility === 'one',
    then: yup.string().required('Veuillez sélectionner une institution'),
    otherwise: yup.string(),
  }),
  'search-institution': yup.string(),
})

export default validationSchema
