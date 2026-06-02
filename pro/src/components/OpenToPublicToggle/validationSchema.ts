import * as yup from 'yup'

export const openToPublicValidationSchema = yup.object().shape({
  isOpenToPublic: yup
    .string()
    .nullable()
    .required('Veuillez sélectionner une option'),
})
