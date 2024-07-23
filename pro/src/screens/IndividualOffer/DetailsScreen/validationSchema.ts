import * as yup from 'yup'

import { DEFAULT_DETAILS_FORM_VALUES } from './constants'

export const validationSchema = yup.object().shape({
  name: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string(),
  author: yup.string(),
  performer: yup.string(),
  ean: yup
    .string()
    .matches(/^\d*$/, "L'EAN doit être composé de 13 chiffres")
    .test({
      message: "L'EAN doit être composé de 13 chiffres",
      test: (ean) => ean === undefined || ean.length === 13,
    }),
  speaker: yup.string(),
  stageDirector: yup.string(),
  visa: yup.string(),
  durationMinutes: yup.string().when('subcategoryConditionalFields', {
    is: (subcategoryConditionalFields: string[]) =>
      subcategoryConditionalFields.includes('durationMinutes'),
    then: (schema) =>
      schema.matches(
        /^\d{1,3}:\d{2}$/,
        'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
      ),
  }),
  categoryId: yup.string().required('Veuillez sélectionner une catégorie'),
  subcategoryId: yup.string().when('categoryId', {
    is: (categoryId: string) => categoryId,
    then: (schema) =>
      schema.required('Veuillez sélectionner une sous-catégorie'),
  }),

  showType: yup.string().when('subcategoryConditionalFields', {
    is: (subcategoryConditionalFields: string[]) =>
      subcategoryConditionalFields.includes('showType'),
    then: (schema) =>
      schema.required('Veuillez sélectionner un type de spectacle'),
  }),
  showSubType: yup.string().when(['subcategoryConditionalFields', 'showType'], {
    is: (subcategoryConditionalFields: string[], showType: string) =>
      subcategoryConditionalFields.includes('showType') &&
      showType !== DEFAULT_DETAILS_FORM_VALUES.showType,
    then: (schema) =>
      schema.required('Veuillez sélectionner un sous-type de spectacle'),
  }),
  gtl_id: yup.string().when(['subcategoryConditionalFields', 'categoryId'], {
    is: (subcategoryConditionalFields: string[], categoryId: string) => {
      return (
        subcategoryConditionalFields.includes('gtl_id') &&
        categoryId !== 'LIVRE'
      )
    },
    then: (schema) => schema.required('Veuillez sélectionner un genre musical'),
  }),
  venueId: yup.string().required('Veuillez sélectionner un lieu'),
})
