import {
  IEducationalCategory,
  IEducationalSubCategory,
} from 'core/OfferEducational'

interface IFilterEducationalCategoriesResult {
  educationalCategories: IEducationalCategory[]
  educationalSubCategories: IEducationalSubCategory[]
}

export const filterEducationalCategories = ({
  categories,
  subcategories,
}: {
  categories?: Category[]
  subcategories?: SubCategory[]
}): IFilterEducationalCategoriesResult => {
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

  const educationalCategories = filteredCategoriesIds.map(
    (categoryId: Category['id']): IEducationalCategory => {
      const currentCategory = categories.find(
        category => categoryId === category.id
      ) as Category

      return {
        id: currentCategory.id,
        label: currentCategory.proLabel,
      }
    }
  )

  return {
    educationalSubCategories,
    educationalCategories,
  }
}
