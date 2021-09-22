import {
  selectSubcategoriesAndSearchGroups,
  selectSubcategory,
  selectSearchGroup,
  selectSearchGroupBySearchResult,
} from '../categoriesSelectors'

describe('selectSubcategoriesAndSearchGroups', () => {
  it('should return subcategories and searchGroups', () => {
    // given
    const state = {
      data: {
        categories: [{ subcategories: [], searchGroups: [] }],
      },
    }

    // when
    const result = selectSubcategoriesAndSearchGroups(state)

    // then
    expect(result).toStrictEqual([{ subcategories: [], searchGroups: [] }])
  })
})

describe('selectSubcategory', () => {
  it('should return subcategory', () => {
    // given
    const state = {
      data: {
        categories: [{ subcategories: [{ id: 'FILM' }], searchGroups: [] }],
      },
    }
    const offer = { id: 'A9', subcategoryId: 'FILM' }

    // when
    const result = selectSubcategory(state, offer)

    // then
    expect(result).toStrictEqual({ id: 'FILM' })
  })
})

describe('selectSearchGroup', () => {
  it('should return searchGroup', () => {
    // given
    const state = {
      data: {
        categories: [
          {
            subcategories: [{ id: 'subcategoryId', searchGroupName: 'FILM' }],
            searchGroups: [{ name: 'FILM', value: 'film' }],
          },
        ],
      },
    }
    const offer = { id: 'A9', subcategoryId: 'subcategoryId' }

    // when
    const result = selectSearchGroup(state, offer)

    // then
    expect(result).toStrictEqual({ name: 'FILM', value: 'film' })
  })
})

describe('selectSearchGroupBySearchResult', () => {
  it('should return searchGroup', () => {
    // given
    const state = {
      data: {
        categories: [
          {
            subcategories: [],
            searchGroups: [
              { name: 'FILM', value: 'film' },
              { name: 'CINEMA', value: 'cinema' },
            ],
          },
        ],
      },
    }
    const offer = { id: 'A9', searchGroupName: 'FILM' }

    // when
    const result = selectSearchGroupBySearchResult(state, offer)

    // then
    expect(result).toStrictEqual({ name: 'FILM', value: 'film' })
  })
})
