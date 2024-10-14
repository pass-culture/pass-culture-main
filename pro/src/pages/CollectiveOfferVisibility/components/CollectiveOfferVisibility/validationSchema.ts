import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  visibility: yup.string().oneOf(['one', 'all']),
  institution: yup
    .string()
    .required('Veuillez sélectionner un établissement scolaire dans la liste'),
  'search-institution': yup.string(),
})
