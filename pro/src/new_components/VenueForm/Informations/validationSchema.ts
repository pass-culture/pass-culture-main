import * as yup from 'yup'

const validationSchema = {
  publicName: yup.string().required('Veuillez renseigner un nom public'),
}

export default validationSchema
