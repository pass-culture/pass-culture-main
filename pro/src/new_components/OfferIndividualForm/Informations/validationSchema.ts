import * as yup from 'yup'

export const validationSchema = {
  name: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string().max(1000),
  author: yup.string(),
  isbn: yup.string(),
  performer: yup.string(),
  speaker: yup.string(),
  stageDirector: yup.string(),
  visa: yup.string(),
  durationMinutes: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) =>
      subCategoryFields.includes('durationMinutes'),
    then: yup
      .string()
      .trim()
      .matches(
        /^[0-9]{1,3}:[0-9]{2}$/,
        'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
      )
      .test({
        name: 'IsValidMinutes',
        message: 'Une heure ne peut pas avoir plus de 59 minutes',
        test: (value?: string) => {
          const [, minutes] = value ? value.split(':') : []
          return !!(minutes && parseInt(minutes, 10) > 60)
        },
      }),

    otherwise: yup.string(),
  }),
}
