import * as yup from 'yup'

const validationSchema = {
  withdrawalDetails: yup.string().notRequired(),
}

export default validationSchema
