import { OfferStatus, SubcategoryIdEnum } from 'apiClient/v1'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'

import {
  buildCategoryOptions,
  buildShowSubTypeOptions,
  buildSubcategoryConditonalFields,
  buildSubcategoryOptions,
  buildVenueOptions,
  deSerializeDurationMinutes,
  serializeDurationMinutes,
  serializeExtraData,
  setDefaultInitialValues,
  setDefaultInitialValuesFromOffer,
  setFormReadOnlyFields,
} from '../utils'

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

describe('setDefaultInitialValues', () => {
  it('should set default initial values', () => {
    expect(
      setDefaultInitialValues({
        filteredVenues: [venueListItemFactory({}), venueListItemFactory({})],
      })
    ).toStrictEqual({
      author: '',
      categoryId: '',
      description: '',
      durationMinutes: '',
      ean: '',
      gtl_id: '',
      name: '',
      performer: '',
      showSubType: '',
      showType: '',
      speaker: '',
      stageDirector: '',
      subcategoryConditionalFields: [],
      subcategoryId: '',
      venueId: '',
      visa: '',
    })

    expect(
      setDefaultInitialValues({
        filteredVenues: [venueListItemFactory({ id: 666 })],
      })
    ).toStrictEqual(
      expect.objectContaining({
        venueId: '666',
      })
    )
  })
})

describe('setDefaultInitialValuesFromOffer', () => {
  it('should set default initial values from offer', () => {
    expect(
      setDefaultInitialValuesFromOffer({
        offer: getIndividualOfferFactory({
          subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
        }),
        subcategories: [
          subcategoryFactory({ id: SubcategoryIdEnum.SEANCE_CINE }),
        ],
      })
    ).toStrictEqual({
      author: 'Chuck Norris',
      categoryId: 'A',
      description: '',
      durationMinutes: '',
      ean: 'Chuck n’est pas identifiable par un EAN',
      gtl_id: '',
      name: 'Le nom de l’offre 1',
      performer: 'Le Poing de Chuck',
      showSubType: 'PEGI 18',
      showType: 'Cinéma',
      speaker: "Chuck Norris n'a pas besoin de doubleur",
      stageDirector: 'JCVD',
      subcategoryConditionalFields: [],
      subcategoryId: 'SEANCE_CINE',
      venueId: '6',
      visa: 'USA',
    })
  })
})

describe('deSerializeDurationMinutes', () => {
  it('should correctly de serialize duration minutes', () => {
    expect(deSerializeDurationMinutes(0)).toStrictEqual('0:00')
    expect(deSerializeDurationMinutes(21)).toStrictEqual('0:21')
    expect(deSerializeDurationMinutes(183)).toStrictEqual('3:03')
    expect(deSerializeDurationMinutes(1838)).toStrictEqual('30:38')
  })
})

describe('serializeDurationMinutes', () => {
  it('should correctly serialize duration minutes', () => {
    expect(serializeDurationMinutes('')).toStrictEqual(null)
    expect(serializeDurationMinutes('0:00')).toStrictEqual(0)
    expect(serializeDurationMinutes('0:21')).toStrictEqual(21)
    expect(serializeDurationMinutes('3:03')).toStrictEqual(183)
    expect(serializeDurationMinutes('30:38')).toStrictEqual(1838)
  })
})

describe('setFormReadOnlyFields', () => {
  it('should not disable fields when there is no offer ', () => {
    expect(setFormReadOnlyFields(null)).toStrictEqual([])
  })
  it('should disable som fields when updating offer ', () => {
    expect(setFormReadOnlyFields(getIndividualOfferFactory({}))).toStrictEqual([
      'categoryId',
      'subcategoryId',
      'venueId',
    ])
  })

  it('should disable all fields when there offer is rejected or pending', () => {
    const expectedKeys = [
      'name',
      'description',
      'venueId',
      'categoryId',
      'subcategoryId',
      'gtl_id',
      'showType',
      'showSubType',
      'speaker',
      'author',
      'visa',
      'stageDirector',
      'performer',
      'ean',
      'durationMinutes',
      'subcategoryConditionalFields',
    ]

    expect(
      setFormReadOnlyFields(
        getIndividualOfferFactory({
          status: OfferStatus.REJECTED,
        })
      )
    ).toStrictEqual(expectedKeys)
    expect(
      setFormReadOnlyFields(
        getIndividualOfferFactory({
          status: OfferStatus.PENDING,
        })
      )
    ).toStrictEqual(expectedKeys)
  })

  it('should disable all fields for provided offers', () => {
    const expectedKeys = [
      'name',
      'description',
      'venueId',
      'categoryId',
      'subcategoryId',
      'gtl_id',
      'showType',
      'showSubType',
      'speaker',
      'author',
      'visa',
      'stageDirector',
      'performer',
      'ean',
      'durationMinutes',
      'subcategoryConditionalFields',
    ]

    expect(
      setFormReadOnlyFields(
        getIndividualOfferFactory({
          lastProvider: { name: 'provider' },
        })
      )
    ).toStrictEqual(expectedKeys)
  })
})

describe('serializeExtraData', () => {
  it('should correctly serialize extra data', () => {
    const formValues = {
      name: 'anything',
      description: 'anything',
      venueId: 'anything',
      categoryId: 'anything',
      subcategoryId: 'anything',
      showType: 'a showtype',
      showSubType: 'a showSubtype',
      gtl_id: 'a gtl id',
      author: 'Boris Vian',
      performer: 'Marcel et son orchestre',
      ean: 'any ean',
      speaker: 'Robert Smith',
      stageDirector: 'Bob Sinclar',
      visa: '123456789',
      durationMinutes: '',
      subcategoryConditionalFields: [],
    }

    expect(serializeExtraData(formValues)).toStrictEqual({
      author: 'Boris Vian',
      ean: 'any ean',
      gtl_id: 'a gtl id',
      performer: 'Marcel et son orchestre',
      showSubType: 'a showSubtype',
      showType: 'a showtype',
      speaker: 'Robert Smith',
      stageDirector: 'Bob Sinclar',
      visa: '123456789',
    })
  })

  it('should correctly serialize extra data with empty values', () => {
    const formValues = {
      name: '',
      description: '',
      venueId: '',
      categoryId: '',
      subcategoryId: '',
      showType: '',
      showSubType: '',
      gtl_id: '',
      author: '',
      performer: '',
      ean: '',
      speaker: '',
      stageDirector: '',
      visa: '',
      durationMinutes: '',
      subcategoryConditionalFields: [],
    }

    expect(serializeExtraData(formValues)).toStrictEqual({})
  })
})
