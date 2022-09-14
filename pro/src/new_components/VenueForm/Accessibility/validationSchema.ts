import * as yup from 'yup'

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

export const validationSchema = {
  accessibility: yup
    .object()
    .test({
      name: 'is-one-true',
      message: 'Veuillez sélectionner au moins un critère d’accessibilité',
      test: isOneTrue,
    })
    .shape({
      mental: yup.boolean(),
      audio: yup.boolean(),
      visual: yup.boolean(),
      motor: yup.boolean(),
      none: yup.boolean(),
    }),
}

export default validationSchema
