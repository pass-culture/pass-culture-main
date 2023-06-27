import {
  EducationalCategory,
  EducationalSubCategory,
} from 'core/OfferEducational'

const categoryFactory = (
  categoryExtend: Partial<EducationalCategory>
): EducationalCategory => ({
  id: 'CATEGORY_ID',
  label: 'categoryLabel',
  ...categoryExtend,
})

export const categoriesFactory = (
  categoriesExtend: Partial<EducationalCategory>[]
): EducationalCategory[] => categoriesExtend.map(categoryFactory)

const subCategoryFactory = (
  subCategoryExtend: Partial<EducationalSubCategory>
): EducationalSubCategory => ({
  id: 'SUB_CATEGORY_ID',
  categoryId: 'CATEGORY_ID',
  label: 'subCategoryLabel',
  ...subCategoryExtend,
})

export const subCategoriesFactory = (
  subCategoriesExtend: Partial<EducationalSubCategory>[]
): EducationalSubCategory[] => subCategoriesExtend.map(subCategoryFactory)
