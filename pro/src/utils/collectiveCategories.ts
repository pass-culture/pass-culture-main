import { CategoriesResponseModel } from 'apiClient/adage'
import { Option } from 'pages/AdageIframe/app/types'

export const filterEducationalSubCategories = ({
  categories,
  subcategories,
}: CategoriesResponseModel): Option<string[]>[] => {
  if (!subcategories || !categories) {
    return []
  }
  return categories.map((category) => ({
    value: subcategories
      .filter((subcategory) => subcategory.categoryId == category.id)
      .map((subcategory) => subcategory.id),
    label: category.proLabel,
  }))
}

export const inferCategoryLabelsFromSubcategories = (
  subCategories: string[][],
  categoriesOptions: Option<string[]>[]
): string[] => {
  const categoryLabels = subCategories
    .map((subCategories) => {
      return subCategories.map((subcategory) => {
        const categoryOption = categoriesOptions.find((option) =>
          option.value.includes(subcategory)
        )
        return categoryOption ? categoryOption.label : ''
      })
    })
    .flat()

  return [...new Set(categoryLabels)]
}
