import * as yup from 'yup'

export const validationSchema = () =>
  yup.object().shape({
    siren: yup
      .string()
      .test(
        'sirenMaybeRequired',
        'Veuillez renseigner le siren de votre entreprise',
        value => {
          return Boolean(value)
        }
      )
      .min(9, 'Le SIREN doit comporter 9 caractères.')
      .max(11, 'Le SIREN doit comporter 9 caractères.'),
  })
