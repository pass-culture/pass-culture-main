import * as yup from 'yup'

const validationSchema = yup.object().shape({
  firstName: yup.string().max(128).required('Veuillez renseigner votre nom'),
  lastName: yup.string().max(128).required('Veuillez renseigner votre prénom'),
})

export default validationSchema
