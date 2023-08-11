import * as yup from 'yup'

const validationSchema = {
  name: yup
    .string()
    .required(`Veuillez renseigner la raison sociale de votre lieu`),
}

export default validationSchema
