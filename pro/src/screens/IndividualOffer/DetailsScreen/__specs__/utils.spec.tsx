import { is } from 'date-fns/locale'
import {
  buildCategoryOptions,
  buildShowSubTypeOptions,
  buildSubcategoryConditonalFields,
  buildSubcategoryOptions,
  buildVenueOptions,
} from '../utils'
import { SubcategoryResponseModel } from 'apiClient/adage'
import {
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'

describe('buildCategoryOptions', () => {
  it('should build category options', () => {
    const categories = [
      {
        id: '1',
        proLabel: 'BB Une catégorie',
        isSelectable: true,
      },
      {
        id: '2',
        proLabel: 'Z une autre catégorie',
        isSelectable: true,
      },
      {
        id: '3',
        proLabel: 'AA une catégorie',
        isSelectable: true,
      },
      {
        id: '4',
        proLabel: 'CC une catégorie',
        isSelectable: false,
      },
    ]

    const result = buildCategoryOptions(categories)

    expect(result).toStrictEqual([
      {
        label: 'AA une catégorie',
        value: '3',
      },
      {
        label: 'BB Une catégorie',
        value: '1',
      },
      {
        label: 'Z une autre catégorie',
        value: '2',
      },
    ])
  })
})

describe('buildSubcategoryOptions', () => {
  it('should build subcategory options', () => {
    const subcategories = [
      subcategoryFactory({ categoryId: '42', proLabel: 'ZZ' }),
      subcategoryFactory({ categoryId: '43' }),
      subcategoryFactory({ categoryId: '42', proLabel: 'AA' }),
      subcategoryFactory({
        categoryId: '42',
        proLabel: 'AA',
        isSelectable: false,
      }),
    ]
    const categoryId = '42'

    const result = buildSubcategoryOptions(subcategories, categoryId)

    expect(result).toStrictEqual([
      {
        label: 'AA',
        value: '3',
      },
      {
        label: 'ZZ',
        value: '1',
      },
    ])
  })
})

describe('buildShowSubTypeOptions', () => {
  it('should build showSubtypes options', () => {
    expect(buildShowSubTypeOptions('')).toStrictEqual([])
    expect(buildShowSubTypeOptions('something unknown')).toStrictEqual([])
    expect(buildShowSubTypeOptions('1500')).toStrictEqual([
      {
        label: 'Autre',
        value: '-1',
      },
      {
        label: 'Son et lumière',
        value: '1501',
      },
      {
        label: 'Spectacle aquatique',
        value: '1504',
      },
      {
        label: 'Spectacle historique',
        value: '1503',
      },
      {
        label: 'Spectacle sur glace',
        value: '1502',
      },
    ])
  })
})

describe('buildSubcategoryFields', () => {
  it('should build subcategory fields', () => {
    expect(
      buildSubcategoryConditonalFields(subcategoryFactory({ isEvent: true }))
    ).toStrictEqual({ subcategoryConditionalFields: ['durationMinutes'] })
    expect(
      buildSubcategoryConditonalFields(
        subcategoryFactory({
          isEvent: false,
          conditionalFields: ['gtl_id', 'author', 'ean'],
        })
      )
    ).toStrictEqual({
      subcategoryConditionalFields: ['gtl_id', 'author', 'ean'],
    })
  })
})

describe('buildVenueOptions', () => {
  it('should build venues options', () => {
    expect(
      buildVenueOptions([venueListItemFactory({}), venueListItemFactory({})])
    ).toStrictEqual([
      {
        label: 'Sélectionner un lieu',
        value: '',
      },
      {
        label: 'Le nom du lieu 1',
        value: '1',
      },
      {
        label: 'Le nom du lieu 2',
        value: '2',
      },
    ])
  })
})
