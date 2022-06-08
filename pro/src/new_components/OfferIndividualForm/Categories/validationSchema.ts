import * as yup from 'yup'

import { CATEGORIES_DEFAULT_VALUES } from './constants'

const validationSchema = {
  categoryId: yup.string().required('Veuillez sélectionner une catégorie'),
  subcategoryId: yup.string().when('categoryId', {
    is: (categoryId: string) => categoryId !== undefined,
    then: yup.string().required('Veuillez sélectionner une sous-catégorie'),
    otherwise: yup.string(),
  }),
  musicType: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) =>
      subCategoryFields.includes('musicType'),
    then: yup.string().required('Veuillez sélectionner une genre musical'),
    otherwise: yup.string(),
  }),
  musicSubType: yup.string().when(['subCategoryFields', 'musicType'], {
    is: (subCategoryFields: string[], musicType: string) =>
      subCategoryFields.includes('musicType') &&
      musicType !== CATEGORIES_DEFAULT_VALUES.musicType,
    then: yup.string().required('Veuillez sélectionner une sous-genre musical'),
    otherwise: yup.string(),
  }),
  showType: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) => subCategoryFields.includes('showType'),
    then: yup.string().required('Veuillez sélectionner un type de spectacle'),
    otherwise: yup.string(),
  }),
  showSubType: yup.string().when(['subCategoryFields', 'showType'], {
    is: (subCategoryFields: string[], showType: string) =>
      subCategoryFields.includes('showType') &&
      showType !== CATEGORIES_DEFAULT_VALUES.showType,
    then: yup
      .string()
      .required('Veuillez sélectionner un sous-type de spectacle'),
    otherwise: yup.string(),
  }),
}

export default validationSchema
