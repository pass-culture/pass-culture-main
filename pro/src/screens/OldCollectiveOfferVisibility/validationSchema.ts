import * as yup from 'yup'

const validationSchema = yup.object().shape({
  visibility: yup.string().oneOf(['one', 'all']),
  institution: yup.string().when('visibility', {
    is: (visibility: string) => visibility === 'one',
    then: schema =>
      schema.required(
        'Veuillez sélectionner un établissement scolaire dans la liste'
      ),
  }),
  'search-institution': yup.string(),
})

export default validationSchema
