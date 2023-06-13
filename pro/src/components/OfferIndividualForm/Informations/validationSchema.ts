import * as yup from 'yup'

export const validationSchema = {
  name: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string().max(1000),
  author: yup.string(),
  isbn: yup.string(),
  performer: yup.string(),
  ean: yup
    .string()
    .matches(/^\d*$/, "L'EAN doit être composé de 13 chiffres")
    .test({
      message: "L'EAN doit être composé de 13 chiffres",
      test: ean => ean === undefined || ean.length === 13,
    }),
  speaker: yup.string(),
  stageDirector: yup.string(),
  visa: yup.string(),
  durationMinutes: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) =>
      subCategoryFields.includes('durationMinutes'),
    then: schema =>
      schema.matches(
        /^\d{1,3}:\d{2}$/,
        'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
      ),
  }),
}
