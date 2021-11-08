import { Category, SubCategory } from "custom_types/categories"

const groupSubCategoriesByCategoryId = (subCategories: SubCategory[]) => {
  const subCategoriesGrouppedByCategoryId: Record<string, SubCategory[]> = {}
  
  subCategories.forEach(subCategory => {
    subCategoriesGrouppedByCategoryId[subCategory.categoryId] = [
      ...(subCategoriesGrouppedByCategoryId[subCategory.categoryId] ?? []),
      subCategory
    ]
  })

  return subCategoriesGrouppedByCategoryId
}

export const getEducationalCategories = (categories?: Category[], subCategories?: SubCategory[]): Category[] => {
  if (!subCategories || !categories) {
    return []
  }

  const subCategoriesGrouppedByCategoryId = groupSubCategoriesByCategoryId(subCategories)

  return categories.filter(category => 
    subCategoriesGrouppedByCategoryId[category.id]?.some(
      subcategory => subcategory.canBeEducational === true
    )
  )
}

export const getEducationalSubCategories = (subCategories?: SubCategory[]): SubCategory[] => {
  if (!subCategories) {
    return []
  }

  return subCategories.filter(subCategory => subCategory.canBeEducational === true)
}
