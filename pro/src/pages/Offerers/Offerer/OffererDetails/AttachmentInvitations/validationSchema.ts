import * as yup from 'yup'

export const validationSchema = () =>
  yup.object().shape({
    email: yup
      .string()
      .max(120)
      .email('Veuillez renseigner un email valide')
      .required('Veuillez renseigner une adresse email'),
  })
