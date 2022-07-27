import * as yup from 'yup'

const validationSchema = yup.object().shape({
  firstName: yup.string().max(128).required(),
  lastName: yup.string().max(128).required(),
})

export default validationSchema
