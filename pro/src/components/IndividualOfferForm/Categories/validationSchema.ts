import * as yup from 'yup'

import { CATEGORIES_DEFAULT_VALUES } from './constants'

const validationSchema = {
  categoryId: yup.string().required('Veuillez sélectionner une catégorie'),
  subcategoryId: yup.string().when('categoryId', {
    is: (categoryId: string) => categoryId !== undefined,
    then: (schema) =>
      schema.required('Veuillez sélectionner une sous-catégorie'),
  }),
  gtl_id: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) => subCategoryFields.includes('gtl_id'),
    then: (schema) => schema.required('Veuillez sélectionner un genre musical'),
  }),
  showType: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) => subCategoryFields.includes('showType'),
    then: (schema) =>
      schema.required('Veuillez sélectionner un type de spectacle'),
  }),
  showSubType: yup.string().when(['subCategoryFields', 'showType'], {
    is: (subCategoryFields: string[], showType: string) =>
      subCategoryFields.includes('showType') &&
      showType !== CATEGORIES_DEFAULT_VALUES.showType,
    then: (schema) =>
      schema.required('Veuillez sélectionner un sous-type de spectacle'),
  }),
}

export default validationSchema
