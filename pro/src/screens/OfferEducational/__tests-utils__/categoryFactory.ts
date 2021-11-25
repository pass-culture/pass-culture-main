import { IEducationalCategory } from 'core/OfferEducational'

const categoryFactory = (
  categoryExtend: Partial<IEducationalCategory>
): IEducationalCategory => {
  return {
    id: 'CATEGORY_ID',
    label: 'categoryLabel',
    ...categoryExtend,
  }
}

export const categoriesFactory = (
  categoriesExtend: Partial<IEducationalCategory>[]
): IEducationalCategory[] => categoriesExtend.map(categoryFactory)
