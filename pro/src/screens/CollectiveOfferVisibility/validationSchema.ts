import * as yup from 'yup'

const validationSchema = yup.object().shape({
  visibility: yup.string().oneOf(['one', 'all']),
  /*institution: yup.string().when('visibility', {
    is: (visibility: string) => visibility === 'one',
    then: yup.string().required('Veuillez sélectionner une institution'),
    otherwise: yup.string(),
  }),*/
  institution: yup.array().when('visibility', {
    is: (visibility: string) => visibility === 'one',
    then: yup.array().min(1),
  }),
  'search-institution': yup.string(),
})

export default validationSchema
/*.when('visibility', {
    is: (visibility: string) => {
      console.log('visibility', visibility === 'one')
      return visibility === 'one'
    },
    then: yup.string().when('institution', (institution, schema) => {
      console.log('institution', institution)
      return schema.test({
        name: 'search-institution-invalid',
        message: 'error',
        test: (): boolean => (institution.length === 0 ? false : true),
      })
    }),
  }),*/
