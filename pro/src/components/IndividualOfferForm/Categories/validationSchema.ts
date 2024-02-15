import * as yup from 'yup'

import { CATEGORIES_DEFAULT_VALUES } from './constants'

export const getValidationSchema = (
  isTiteliveMusicGenreFeatureEnabled: boolean
) => {
  const musicTypeFieldsValidator = isTiteliveMusicGenreFeatureEnabled
    ? {
        gtl_id: yup.string().when(['subCategoryFields', 'categoryId'], {
          is: (subCategoryFields: string[], categoryId: string) => {
            return (
              subCategoryFields.includes('gtl_id') && categoryId !== 'LIVRE'
            )
          },
          then: (schema) =>
            schema.required('Veuillez sélectionner un genre musical'),
        }),
        musicType: yup.string(),
        musicSubType: yup.string(),
      }
    : {
        gtl_id: yup.string(),
        musicType: yup.string().when('subCategoryFields', {
          is: (subCategoryFields: string[]) =>
            subCategoryFields.includes('musicType'),
          then: (schema) =>
            schema.required('Veuillez sélectionner un genre musical'),
        }),
        musicSubType: yup.string().when(['subCategoryFields', 'musicType'], {
          is: (subCategoryFields: string[], musicType: string) =>
            subCategoryFields.includes('musicType') &&
            musicType !== CATEGORIES_DEFAULT_VALUES.musicType,
          then: (schema) =>
            schema.required('Veuillez sélectionner un sous-genre musical'),
        }),
      }

  return {
    categoryId: yup.string().required('Veuillez sélectionner une catégorie'),
    subcategoryId: yup.string().when('categoryId', {
      is: (categoryId: string) => categoryId !== undefined,
      then: (schema) =>
        schema.required('Veuillez sélectionner une sous-catégorie'),
    }),

    showType: yup.string().when('subCategoryFields', {
      is: (subCategoryFields: string[]) =>
        subCategoryFields.includes('showType'),
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
    ...musicTypeFieldsValidator,
  }
}

export default getValidationSchema
