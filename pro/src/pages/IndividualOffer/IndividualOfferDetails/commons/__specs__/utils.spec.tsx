import { OfferStatus, SubcategoryIdEnum } from 'apiClient/v1'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'commons/utils/factories/individualApiFactories'

import { DEFAULT_DETAILS_FORM_VALUES } from '../constants'
import {
  buildCategoryOptions,
  buildShowSubTypeOptions,
  buildSubcategoryOptions,
  completeSubcategoryConditionalFields,
  deSerializeDurationMinutes,
  formatVenuesOptions,
  hasMusicType,
  serializeDetailsPostData,
  serializeDurationMinutes,
  serializeExtraData,
  setDefaultInitialValuesFromOffer,
  setFormReadOnlyFields,
} from '../utils'

describe('hasMusicType', () => {
  it('should return true if categoryId=LIVRE and has a musicType as a conditional field', () =>
    expect(hasMusicType('LIVRE', ['musicType'])).toBe(true))
  it('should return true if categoryId!=LIVRE and has a gtl_id as a conditional field', () =>
    expect(hasMusicType('AUTRE', ['gtl_id'])).toBe(true))
  it('should return false otherwise', () =>
    expect(hasMusicType('AUTRE', ['musicType'])).toBe(false))
})

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
      completeSubcategoryConditionalFields(
        subcategoryFactory({ isEvent: true })
      )
    ).toStrictEqual(['durationMinutes'])
    expect(
      completeSubcategoryConditionalFields(
        subcategoryFactory({
          isEvent: false,
          conditionalFields: ['gtl_id', 'author', 'ean'],
        })
      )
    ).toStrictEqual(['gtl_id', 'author', 'ean'])
  })
})

describe('formatVenuesOptions', () => {
  it('should format venues as options', () => {
    const formattedVenuesOptions = formatVenuesOptions(
      [
        venueListItemFactory({ isVirtual: false, id: 10 }),
        venueListItemFactory({ isVirtual: false, id: 3 }),
      ],
      false
    )
    expect(formattedVenuesOptions).toEqual(
      expect.arrayContaining([expect.objectContaining({ value: '10' })])
    )

    expect(formattedVenuesOptions).toEqual(
      expect.arrayContaining([expect.objectContaining({ value: '3' })])
    )
  })

  it('should exclude digital venues if a physcal venue is available', () => {
    const formattedVenuesOptions = formatVenuesOptions(
      [
        venueListItemFactory({ isVirtual: true, id: 10 }),
        venueListItemFactory({ isVirtual: false, id: 3 }),
      ],
      false
    )
    expect(formattedVenuesOptions).not.toEqual(
      expect.arrayContaining([expect.objectContaining({ value: '10' })])
    )

    expect(formattedVenuesOptions).toEqual(
      expect.arrayContaining([expect.objectContaining({ value: '3' })])
    )

    const formattedDigitalVenuesOptions = formatVenuesOptions(
      [venueListItemFactory({ isVirtual: true, id: 10 })],
      true
    )
    expect(formattedDigitalVenuesOptions).toEqual(
      expect.arrayContaining([expect.objectContaining({ value: '10' })])
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
      ean: '1234567891234',
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
      productId: '',
      url: undefined,
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

describe('setFormReadOnlyFields', () => {
  it('should disable all fields except venue when an ean search filled the form and offer is not yet created', () => {
    const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES).filter(
      (key) => key !== 'venueId'
    )

    expect(setFormReadOnlyFields(null, true)).toStrictEqual(expectedValues)
  })

  it('should disable all field when offer has been created and was created by ean', () => {
    const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

    expect(
      setFormReadOnlyFields(getIndividualOfferFactory({ productId: 1 }), true)
    ).toStrictEqual(expectedValues)
  })

  it('should not disable fields when there is no offer and no ean search was performed', () => {
    expect(setFormReadOnlyFields(null)).toStrictEqual([])
  })

  it('should disable category/subcategory/venue fields when updating a regular offer', () => {
    expect(setFormReadOnlyFields(getIndividualOfferFactory({}))).toStrictEqual([
      'categoryId',
      'subcategoryId',
      'venueId',
    ])
  })

  it('should disable all fields when there offer is rejected or pending', () => {
    const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

    expect(
      setFormReadOnlyFields(
        getIndividualOfferFactory({
          status: OfferStatus.REJECTED,
        })
      )
    ).toStrictEqual(expectedValues)

    expect(
      setFormReadOnlyFields(
        getIndividualOfferFactory({
          status: OfferStatus.PENDING,
        })
      )
    ).toStrictEqual(expectedValues)
  })

  it('should disable all fields for provided offers', () => {
    const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

    expect(
      setFormReadOnlyFields(
        getIndividualOfferFactory({
          lastProvider: { name: 'provider' },
        })
      )
    ).toStrictEqual(expectedValues)
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
      productId: '',
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
      productId: '',
    }

    expect(serializeExtraData(formValues)).toStrictEqual({
      author: '',
      ean: '',
      gtl_id: '',
      performer: '',
      showSubType: '',
      showType: '',
      speaker: '',
      stageDirector: '',
      visa: '',
    })
  })
})

describe('serializeDetailsPostData', () => {
  it('should trim spaces in all string fields', () => {
    const formValues = {
      name: ' Festival de la Musique ',
      description: ' Ancien festival annuel musical ',
      venueId: '0',
      categoryId: 'anything',
      subcategoryId: 'anything',
      showType: 'a showtype',
      showSubType: 'a showSubtype',
      gtl_id: 'a gtl id',
      author: ' Boris Vian ',
      performer: ' Marcel et son orchestre ',
      ean: ' any ean ',
      speaker: ' Robert Smith ',
      stageDirector: ' Bob Sinclar ',
      visa: ' 123456789 ',
      durationMinutes: '',
      subcategoryConditionalFields: [],
      productId: '',
    }

    expect(serializeDetailsPostData(formValues)).toStrictEqual({
      name: 'Festival de la Musique',
      subcategoryId: 'anything',
      venueId: 0,
      description: 'Ancien festival annuel musical',
      durationMinutes: undefined,
      extraData: {
        author: 'Boris Vian',
        gtl_id: 'a gtl id',
        performer: 'Marcel et son orchestre',
        showType: 'a showtype',
        showSubType: 'a showSubtype',
        speaker: 'Robert Smith',
        stageDirector: 'Bob Sinclar',
        visa: '123456789',
        ean: 'any ean',
      },
      url: undefined,
      productId: undefined,
    })
  })
})

describe('serializeDurationMinutes', () => {
  it('should return undefined when durationHour is empty', () => {
    expect(serializeDurationMinutes('')).toStrictEqual(undefined)
  })

  it('should transform string duration into int minutes', () => {
    expect(serializeDurationMinutes('0:00')).toStrictEqual(0)
    expect(serializeDurationMinutes('0:21')).toStrictEqual(21)
    expect(serializeDurationMinutes('3:03')).toStrictEqual(183)
    expect(serializeDurationMinutes('30:38')).toStrictEqual(1838)
  })
})
