import {
  type ArtistOfferLinkResponseModel,
  ArtistType,
  DisplayableActivity,
  OfferStatus,
  SubcategoryIdEnum,
} from '@/apiClient/v1/new'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { getOfferLastProvider } from '@/commons/utils/factories/providerFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { DEFAULT_DETAILS_FORM_VALUES } from '../constants'
import {
  buildCategoryOptions,
  buildShowSubTypeOptions,
  buildSubcategoryOptions,
  completeSubcategoryConditionalFields,
  getAccessibilityFormValuesFromOffer,
  getFormReadOnlyFields,
  getInitialArtistOfferLinks,
  getInitialValuesFromOffer,
  getInitialValuesFromVenue,
  hasMusicType,
  isSubCategoryCD,
} from '../utils'

const defaultVenue = makeGetVenueResponseModel({ id: 1 })

describe('isSubCategoryCD', () => {
  it('should return true for SUPPORT_PHYSIQUE_MUSIQUE_CD subcategory', () => {
    expect(isSubCategoryCD(SubcategoryIdEnum.SUPPORT_PHYSIQUE_MUSIQUE_CD)).toBe(
      true
    )
  })

  it('should return false for any other subcategory', () => {
    expect(isSubCategoryCD(SubcategoryIdEnum.SEANCE_CINE)).toBe(false)
    expect(isSubCategoryCD('')).toBe(false)
  })
})

describe('hasMusicType', () => {
  it('should return true if categoryId=LIVRE and has a musicType as a conditional field', () =>
    expect(hasMusicType('LIVRE', ['musicType'])).toBe(true))
  it('should return true if categoryId!=LIVRE and has a gtl_id as a conditional field', () =>
    expect(hasMusicType('AUTRE', ['gtl_id'])).toBe(true))
  it('should return false for LIVRE without musicType conditional field', () =>
    expect(hasMusicType('LIVRE', ['gtl_id'])).toBe(false))
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
  it('should return an empty array when showType is undefined', () => {
    expect(buildShowSubTypeOptions(undefined)).toStrictEqual([])
  })

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
  it('should return an empty array when subcategory is undefined', () => {
    expect(completeSubcategoryConditionalFields(undefined)).toStrictEqual([])
  })

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

describe('getInitialArtistOfferLinks', () => {
  const defaultLinks = DEFAULT_DETAILS_FORM_VALUES.artistOfferLinks

  it('should return defaults links', () => {
    const artists: ArtistOfferLinkResponseModel[] = []

    // @ts-expect-error - waiting Artist migration on pydantic V2
    const result = getInitialArtistOfferLinks(artists, defaultLinks)

    expect(result).toStrictEqual(defaultLinks)
  })

  it('should return offer links', () => {
    const offerLinks: ArtistOfferLinkResponseModel[] = [
      { artistId: '1', artistName: 'Author A', artistType: ArtistType.AUTHOR },
      {
        artistId: '2',
        artistName: 'Performer B',
        artistType: ArtistType.PERFORMER,
      },
      {
        artistId: '3',
        artistName: 'Director C',
        artistType: ArtistType.STAGE_DIRECTOR,
      },
    ]
    // @ts-expect-error - waiting Artist migration on pydantic V2
    const result = getInitialArtistOfferLinks(offerLinks, defaultLinks)

    expect(result).toStrictEqual(offerLinks)
  })

  it('should add missing artist types from defaults to offer links', () => {
    const offerLinks: ArtistOfferLinkResponseModel[] = [
      { artistId: '1', artistName: 'Author A', artistType: ArtistType.AUTHOR },
    ]

    // @ts-expect-error - waiting Artist migration on pydantic V2
    const result = getInitialArtistOfferLinks(offerLinks, defaultLinks)

    expect(result).toHaveLength(3)
    expect(result[0]).toStrictEqual(offerLinks[0])
    expect(result[1]).toStrictEqual(defaultLinks[1])
    expect(result[2]).toStrictEqual(defaultLinks[2])
  })
})

describe('getInitialValuesFromVenue', () => {
  it('should return default form values with venue id and accessibility from the venue', () => {
    const venue = makeGetVenueResponseModel({
      id: 42,
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: false,
    })

    const result = getInitialValuesFromVenue(venue)

    expect(result).toStrictEqual({
      ...DEFAULT_DETAILS_FORM_VALUES,
      venueId: '42',
      accessibility: {
        audio: true,
        mental: false,
        motor: true,
        visual: false,
        none: false,
      },
    })
  })
})

describe('getInitialValuesFromOffer', () => {
  it('should get the expected initial values from an offer with accessibility', () => {
    const offer = getIndividualOfferFactory({
      id: 1,
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      venue: getOfferVenueFactory({ id: 6 }),
      visualDisabilityCompliant: false,
    })
    const subcategories = [
      subcategoryFactory({ id: SubcategoryIdEnum.SEANCE_CINE }),
    ]

    const result = getInitialValuesFromOffer({
      offer,
      subcategories,
    })

    expect(result).toStrictEqual({
      author: 'Chuck Norris',
      categoryId: 'A',
      description: '',
      durationMinutes: '',
      ean: '1234567891234',
      gtl_id: '',
      hasCulturalOutreachClaim: false,
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
      artistOfferLinks: [
        {
          artistId: null,
          artistName: '',
          artistType: ArtistType.AUTHOR,
        },
        {
          artistId: null,
          artistName: '',
          artistType: ArtistType.PERFORMER,
        },
        {
          artistId: null,
          artistName: '',
          artistType: ArtistType.STAGE_DIRECTOR,
        },
      ],
      accessibility: {
        audio: true,
        mental: false,
        motor: true,
        none: false,
        visual: false,
      },
    })
  })

  it('should use offer description, durationMinutes and productId when present', () => {
    const offer = getIndividualOfferFactory({
      id: 2,
      description: 'A custom description',
      durationMinutes: 90,
      productId: 456,
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      venue: getOfferVenueFactory({ id: 7 }),
      extraData: {},
    })
    const subcategories = [
      subcategoryFactory({ id: SubcategoryIdEnum.SEANCE_CINE }),
    ]

    const result = getInitialValuesFromOffer({ offer, subcategories })

    expect(result.description).toBe('A custom description')
    expect(result.durationMinutes).toBe('01:30')
    expect(result.productId).toBe('456')
    expect(result.ean).toBe(DEFAULT_DETAILS_FORM_VALUES.ean)
    expect(result.showType).toBe(DEFAULT_DETAILS_FORM_VALUES.showType)
    expect(result.showSubType).toBe(DEFAULT_DETAILS_FORM_VALUES.showSubType)
    expect(result.visa).toBe(DEFAULT_DETAILS_FORM_VALUES.visa)
    expect(result.gtl_id).toBe(DEFAULT_DETAILS_FORM_VALUES.gtl_id)
    expect(result.speaker).toBe(DEFAULT_DETAILS_FORM_VALUES.speaker)
    expect(result.author).toBe(DEFAULT_DETAILS_FORM_VALUES.author)
    expect(result.performer).toBe(DEFAULT_DETAILS_FORM_VALUES.performer)
    expect(result.stageDirector).toBe(DEFAULT_DETAILS_FORM_VALUES.stageDirector)
  })
})

describe('getFormReadOnlyFields', () => {
  it('should disable all fields except venue when an ean search filled the form and offer is not yet created', () => {
    const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES).filter(
      (key) => key !== 'venueId'
    )

    expect(getFormReadOnlyFields(null, true, defaultVenue)).toStrictEqual(
      expectedValues
    )
  })

  it('should disable all field when offer has been created and was created by ean', () => {
    const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

    expect(
      getFormReadOnlyFields(
        getIndividualOfferFactory({ productId: 1 }),
        true,
        defaultVenue
      )
    ).toStrictEqual(expectedValues)
  })

  it('should not disable fields when there is no offer and no ean search was performed', () => {
    expect(getFormReadOnlyFields(null, false, defaultVenue)).toStrictEqual([])
  })

  it('should disable category/subcategory/venue fields when updating a regular offer', () => {
    expect(
      getFormReadOnlyFields(getIndividualOfferFactory({}), false, defaultVenue)
    ).toStrictEqual(['categoryId', 'subcategoryId', 'venueId'])
  })

  it('should disable all fields except hasCulturalOutreachClaim for synchronized offers', () => {
    const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES).filter(
      (key) => key !== 'hasCulturalOutreachClaim'
    )

    expect(
      getFormReadOnlyFields(
        getIndividualOfferFactory({
          lastProvider: { name: 'provider' },
        }),
        false,
        defaultVenue
      )
    ).toStrictEqual(expectedValues)
  })

  it('should disable all fields except name, description and hasCulturalOutreachClaim for synchronized offers when the venue is a museum', () => {
    const expectedValues = [
      'venueId',
      'categoryId',
      'subcategoryId',
      'gtl_id',
      'showType',
      'showSubType',
      'speaker',
      'author',
      'artistOfferLinks',
      'visa',
      'stageDirector',
      'performer',
      'ean',
      'durationMinutes',
      'subcategoryConditionalFields',
      'productId',
    ]

    expect(
      getFormReadOnlyFields(
        getIndividualOfferFactory({
          lastProvider: { name: 'provider' },
        }),
        false,
        makeGetVenueResponseModel({
          id: 1,
          activity: DisplayableActivity.MUSEUM,
        })
      )
    ).toStrictEqual(expectedValues)
  })

  it('should include accessibility as read-only when the offer status is pending or rejected', () => {
    const pendingOffer = getIndividualOfferFactory({
      status: OfferStatus.PENDING,
    })
    const rejectedOffer = getIndividualOfferFactory({
      status: OfferStatus.REJECTED,
    })

    let isProductBased = false

    expect(
      getFormReadOnlyFields(pendingOffer, isProductBased, defaultVenue)
    ).toContain('accessibility')
    expect(
      getFormReadOnlyFields(rejectedOffer, isProductBased, defaultVenue)
    ).toContain('accessibility')

    isProductBased = true

    expect(
      getFormReadOnlyFields(pendingOffer, isProductBased, defaultVenue)
    ).toContain('accessibility')
    expect(
      getFormReadOnlyFields(rejectedOffer, isProductBased, defaultVenue)
    ).toContain('accessibility')
  })

  it('should exclude accessibility for all other cases', () => {
    const nullOffer = null
    const synchronizedOffer = getIndividualOfferFactory({
      lastProvider: getOfferLastProvider(),
    })

    let isProductBased = false

    expect(
      getFormReadOnlyFields(nullOffer, isProductBased, defaultVenue)
    ).not.toContain('accessibility')
    expect(
      getFormReadOnlyFields(synchronizedOffer, isProductBased, defaultVenue)
    ).not.toContain('accessibility')

    isProductBased = true

    expect(
      getFormReadOnlyFields(nullOffer, isProductBased, defaultVenue)
    ).not.toContain('accessibility')
    expect(
      getFormReadOnlyFields(synchronizedOffer, isProductBased, defaultVenue)
    ).not.toContain('accessibility')
  })
})

describe('getAccessibilityFormValuesFromOffer', () => {
  it('should coerce all flags to false and set none as true when flags are all false, null or undefined', () => {
    const offer = getIndividualOfferFactory({
      // TODO (tpommellet) to remove once GetIndividualOfferWithAddressResponseModel is migrated to Pydantic V2
      // @ts-expect-error
      audioDisabilityCompliant: null,
      mentalDisabilityCompliant: undefined,
      motorDisabilityCompliant: false,
      visualDisabilityCompliant: false,
    })

    expect(getAccessibilityFormValuesFromOffer(offer)).toEqual({
      audio: false,
      mental: false,
      motor: false,
      visual: false,
      none: true,
    })
  })

  it('should return correct flags and set none as false when any flags is true', () => {
    const offer = getIndividualOfferFactory({
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: false,
      visualDisabilityCompliant: false,
    })

    const result = getAccessibilityFormValuesFromOffer(offer)

    expect(result).toEqual({
      audio: false,
      mental: true,
      motor: false,
      visual: false,
      none: false,
    })
  })
})
