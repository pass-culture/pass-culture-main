import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .email('Veuillez renseigner un e-mail valide')
    .required('Veuillez renseigner une adresse e-mail'),
  password: yup.string().required('Veuillez renseigner un mot de passe'),
})
