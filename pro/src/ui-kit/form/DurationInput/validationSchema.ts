import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  durationMinutes: yup.string().trim(),
})
