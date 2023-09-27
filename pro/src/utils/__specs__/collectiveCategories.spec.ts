import {
  filterEducationalSubCategories,
  inferCategoryLabelsFromSubcategories,
} from 'utils/collectiveCategories'

describe('filterEducationalSubCategories', () => {
  it('should return category labels and subcategories', () => {
    const categoriesResponse = {
      categories: [
        { id: 'cat1', proLabel: 'Category 1' },
        { id: 'cat2', proLabel: 'Category 2' },
      ],
      subcategories: [
        { id: 'subcat1', categoryId: 'cat1' },
        { id: 'subcat2', categoryId: 'cat1' },
        { id: 'subcat3', categoryId: 'cat2' },
      ],
    }

    const result = filterEducationalSubCategories(categoriesResponse)

    expect(result).toEqual([
      { label: 'Category 1', value: ['subcat1', 'subcat2'] },
      { label: 'Category 2', value: ['subcat3'] },
    ])
  })

  it('should return empty array if categories or subcategories are not defined', () => {
    const categoriesResponse = {
      categories: [],
      subcategories: [],
    }

    const result = filterEducationalSubCategories(categoriesResponse)

    expect(result).toEqual([])
  })
})

describe('inferCategoryLabelsFromSubcategories', () => {
  it('should return category labels given subcategories array', () => {
    const subCategories = [
      ['subcat1', 'subcat2'],
      ['subcat2', 'subcat3'],
    ]

    const categoriesOptions = [
      { label: 'Category 1', value: ['subcat1', 'subcat2'] },
      { label: 'Category 2', value: ['subcat2', 'subcat3'] },
    ]

    const result = inferCategoryLabelsFromSubcategories(
      subCategories,
      categoriesOptions
    )

    expect(result).toEqual(['Category 1', 'Category 2'])
  })
  it('should return empty label if subcatgory does not match any subcategories array', () => {
    const subCategories = [
      ['subcat1', 'subcat2'],
      ['aaa', 'zzz'],
    ]

    const categoriesOptions = [
      { label: 'Category 1', value: ['subcat1', 'subcat2'] },
    ]

    const result = inferCategoryLabelsFromSubcategories(
      subCategories,
      categoriesOptions
    )

    expect(result).toEqual(['Category 1', ''])
  })
})
