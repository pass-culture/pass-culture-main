import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  durationMinutes: yup
    .string()
    .trim()
    .matches(
      /^[0-9]{1,3}:[0-9]{2}$/,
      'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
    ),
})
