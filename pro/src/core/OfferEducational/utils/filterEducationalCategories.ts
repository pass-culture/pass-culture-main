import { CategoriesResponseModel, CategoryResponseModel } from 'apiClient/v1'
import { EducationalCategories } from 'core/OfferEducational'

export const filterEducationalCategories = ({
  categories,
  subcategories,
}: CategoriesResponseModel): EducationalCategories => {
  if (!subcategories || !categories) {
    return {
      educationalCategories: [],
      educationalSubCategories: [],
    }
  }

  const educationalSubCategories = subcategories
    .filter(subCategory => subCategory.canBeEducational === true)
    .filter(subCategory => subCategory.isSelectable === true)
    .map(subCategory => ({
      id: subCategory.id,
      categoryId: subCategory.categoryId,
      label: subCategory.proLabel,
    }))

  const filteredCategoriesIds = Array.from(
    new Set(educationalSubCategories.map(subCategory => subCategory.categoryId))
  )

  const educationalCategories = filteredCategoriesIds.map(categoryId => {
    const currentCategory = categories.find(
      category => categoryId === category.id
    ) as CategoryResponseModel

    return {
      id: currentCategory.id,
      label: currentCategory.proLabel,
    }
  })

  return {
    educationalSubCategories,
    educationalCategories,
  }
}
