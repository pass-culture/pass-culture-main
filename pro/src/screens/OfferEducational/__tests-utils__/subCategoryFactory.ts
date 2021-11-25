import merge from 'lodash/merge'

import { IEducationalSubCategory } from 'core/OfferEducational'

const categoryFactory = (
  subCategoryExtend: Partial<IEducationalSubCategory>
): IEducationalSubCategory =>
  merge(
    {},
    {
      id: 'SUB_CATEGORY_ID',
      categoryId: 'CATEGORY_ID',
      label: 'subCategoryLabel',
    },
    subCategoryExtend
  )

export const subCategoriesFactory = (
  subCategoriesExtend: Partial<IEducationalSubCategory>[]
): IEducationalSubCategory[] => subCategoriesExtend.map(categoryFactory)
