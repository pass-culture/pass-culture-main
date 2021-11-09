import { Category } from "custom_types/categories"

type CategoryExtend = Partial<Category> & { id: string }

const categoryFactory = (categoryExtend: CategoryExtend): Category => {
  return {
    proLabel: 'categoryLabel',
    isSelectable: true,
    ...categoryExtend,
  }
}

export const categoriesFactory = (categoriesExtend: CategoryExtend[]): Category[] => 
  categoriesExtend.map(categoryFactory)
