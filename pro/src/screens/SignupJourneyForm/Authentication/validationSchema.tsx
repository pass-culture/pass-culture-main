import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  siret: yup.string().required(''),
  name: yup.string().required(''),
  publicName: yup.string().nullable(),
})
