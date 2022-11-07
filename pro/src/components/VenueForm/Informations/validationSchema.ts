import * as yup from 'yup'

const validationSchema = {
  name: yup
    .string()
    .required('Veuillez renseigner le nom juridique de votre lieu'),
}

export default validationSchema
