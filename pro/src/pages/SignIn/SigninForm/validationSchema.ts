import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com')
    .required('Veuillez renseigner une adresse email'),
  password: yup.string().required('Veuillez renseigner un mot de passe'),
})
