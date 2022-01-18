import {
  IEducationalCategory,
  IEducationalSubCategory,
} from 'core/OfferEducational'

const categoryFactory = (
  categoryExtend: Partial<IEducationalCategory>
): IEducationalCategory => ({
  id: 'CATEGORY_ID',
  label: 'categoryLabel',
  ...categoryExtend,
})

export const categoriesFactory = (
  categoriesExtend: Partial<IEducationalCategory>[]
): IEducationalCategory[] => categoriesExtend.map(categoryFactory)

const subCategoryFactory = (
  subCategoryExtend: Partial<IEducationalSubCategory>
): IEducationalSubCategory => ({
  id: 'SUB_CATEGORY_ID',
  categoryId: 'CATEGORY_ID',
  label: 'subCategoryLabel',
  ...subCategoryExtend,
})

export const subCategoriesFactory = (
  subCategoriesExtend: Partial<IEducationalSubCategory>[]
): IEducationalSubCategory[] => subCategoriesExtend.map(subCategoryFactory)
