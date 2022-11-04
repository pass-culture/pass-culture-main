import * as yup from 'yup'

const validationSchema = {
  name: yup.string().required('Veuillez renseigner un nom'),
}

export default validationSchema
