import {
  type ArtistOfferLinkResponseModel,
  ArtistType,
  OfferStatus,
  SubcategoryIdEnum,
  type VenueListItemResponseModel,
} from '@/apiClient/v1'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { getOfferLastProvider } from '@/commons/utils/factories/providerFactories'
import { offerVenueFactory } from '@/commons/utils/factories/venueFactories'

import { DEFAULT_DETAILS_FORM_VALUES } from '../constants'
import {
  buildCategoryOptions,
  buildShowSubTypeOptions,
  buildSubcategoryOptions,
  completeSubcategoryConditionalFields,
  filterAvailableVenues,
  getAccessibilityFormValuesFromOffer,
  getFormReadOnlyFields,
  getInitialArtistOfferLinks,
  getInitialValuesFromOffer,
  getInitialValuesFromVenues,
  getVenuesAsOptions,
  hasMusicType,
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

describe('getInitialArtistOfferLinks', () => {
  const defaultLinks = DEFAULT_DETAILS_FORM_VALUES.artistOfferLinks

  it('should return defaults links', () => {
    const artists: ArtistOfferLinkResponseModel[] = []

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

    const result = getInitialArtistOfferLinks(offerLinks, defaultLinks)

    expect(result).toStrictEqual(offerLinks)
  })

  it('should add missing artist types from defaults to offer links', () => {
    const offerLinks: ArtistOfferLinkResponseModel[] = [
      { artistId: '1', artistName: 'Author A', artistType: ArtistType.AUTHOR },
    ]

    const result = getInitialArtistOfferLinks(offerLinks, defaultLinks)

    expect(result).toHaveLength(3)
    expect(result[0]).toStrictEqual(offerLinks[0])
    expect(result[1]).toStrictEqual(defaultLinks[1])
    expect(result[2]).toStrictEqual(defaultLinks[2])
  })
})

describe('filterAvailableVenues', () => {
  const physicalVenue = venueListItemFactory({
    id: 1,
    name: 'Physical Venue',
    isVirtual: false,
  })
  const virtualVenue = venueListItemFactory({
    id: 2,
    name: 'Virtual Venue',
    isVirtual: true,
  })

  it('should return only physical venues if at least one exists', () => {
    const venues = [physicalVenue, virtualVenue]

    const physicalOfferResult = filterAvailableVenues(venues, false)

    expect(physicalOfferResult).toEqual([physicalVenue])

    const virtualOfferResult = filterAvailableVenues(venues, true)

    expect(virtualOfferResult).toEqual([physicalVenue])
  })

  it('should return an empty array for a physical offer with only virtual venues', () => {
    const venues = [virtualVenue]

    const physicalOfferResult = filterAvailableVenues(venues, false)

    expect(physicalOfferResult).toEqual([])
  })

  it('should return virtual venues for a virtual offer if NO physical venues exist', () => {
    const venues = [virtualVenue]

    const virtualOfferResult = filterAvailableVenues(venues, true)

    expect(virtualOfferResult).toEqual([virtualVenue])
  })

  it('should return all physical venues if only physical venues are provided', () => {
    const anotherPhysicalVenue = venueListItemFactory({
      id: 3,
      name: 'Another Physical',
      isVirtual: false,
    })
    const venues = [physicalVenue, anotherPhysicalVenue]

    const physicalOfferResult = filterAvailableVenues(venues, false)

    expect(physicalOfferResult).toEqual(venues)

    const virtualOfferResult = filterAvailableVenues(venues, true)

    expect(virtualOfferResult).toEqual(venues)
  })
})

describe('getVenuesAsOptions', () => {
  it('should correctly map a list of venues to an array of Option objects', () => {
    const venues = [
      venueListItemFactory({ id: 10, publicName: 'My Venue' }),
      venueListItemFactory({ id: 20, publicName: 'Your Venue' }),
    ]
    const options = getVenuesAsOptions(venues)

    expect(options).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ value: '10', label: 'My Venue' }),
        expect.objectContaining({ value: '20', label: 'Your Venue' }),
      ])
    )
    expect(options.length).toBe(2)
  })

  it('should sort the resulting options by label using French locale rules', () => {
    const venues = [
      venueListItemFactory({ publicName: 'Zoo' }),
      venueListItemFactory({ publicName: 'Cinéma' }),
      venueListItemFactory({ publicName: 'À la ferme' }),
    ]

    const optionsResult = getVenuesAsOptions(venues)

    expect(optionsResult.map((o) => o.label)).toEqual([
      'À la ferme',
      'Cinéma',
      'Zoo',
    ])
  })
})

describe('getInitialValuesFromOffer', () => {
  describe('without Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = false

    it('should get the expected initial values from an offer', () => {
      const offer = getIndividualOfferFactory({
        subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
        venue: offerVenueFactory({ id: 6 }),
      })
      const subcategories = [
        subcategoryFactory({ id: SubcategoryIdEnum.SEANCE_CINE }),
      ]

      const result = getInitialValuesFromOffer({
        offer,
        subcategories,
        isNewOfferCreationFlowFeatureActive,
      })

      expect(result).toStrictEqual({
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
      })
    })
  })

  describe('with Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = true

    it('should get the expected initial values from an offer with accessibility', () => {
      const offer = getIndividualOfferFactory({
        id: 1,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: true,
        subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
        venue: offerVenueFactory({ id: 6 }),
        visualDisabilityCompliant: false,
      })
      const subcategories = [
        subcategoryFactory({ id: SubcategoryIdEnum.SEANCE_CINE }),
      ]

      const result = getInitialValuesFromOffer({
        offer,
        subcategories,
        isNewOfferCreationFlowFeatureActive,
      })

      expect(result).toStrictEqual({
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
  })
})

describe('getInitialValuesFromVenues', () => {
  describe('without Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = false

    it('should return a `venueId` if only one is available', () => {
      const venues = [venueListItemFactory({ id: 123 })]

      const initialValuesResult = getInitialValuesFromVenues(
        venues,
        isNewOfferCreationFlowFeatureActive
      )

      expect(initialValuesResult.venueId).toBe('123')
      expect(initialValuesResult).not.toHaveProperty('accessibility')
    })

    it('should return an empty `venueId` if multiple are available', () => {
      const venues = [
        venueListItemFactory({ id: 1 }),
        venueListItemFactory({ id: 2 }),
      ]

      const initialValuesResult = getInitialValuesFromVenues(
        venues,
        isNewOfferCreationFlowFeatureActive
      )

      expect(initialValuesResult.venueId).toBe('')
      expect(initialValuesResult).not.toHaveProperty('accessibility')
    })

    it('should return an empty `venueId` if none are available', () => {
      const venues: VenueListItemResponseModel[] = []

      const initialValuesResult = getInitialValuesFromVenues(
        venues,
        isNewOfferCreationFlowFeatureActive
      )

      expect(initialValuesResult.venueId).toBe('')
      expect(initialValuesResult).not.toHaveProperty('accessibility')
    })
  })

  describe('with Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = true

    it('should return an empty `venueId` and none `accessibility` options if multiple venues are available', () => {
      const venues = [
        venueListItemFactory({ id: 1 }),
        venueListItemFactory({ id: 2 }),
      ]

      const initialValuesResult = getInitialValuesFromVenues(
        venues,
        isNewOfferCreationFlowFeatureActive
      )

      expect(initialValuesResult.venueId).toBe('')
      expect(initialValuesResult.accessibility).toEqual({
        audio: false,
        visual: false,
        motor: false,
        mental: false,
        none: true,
      })
    })

    it('should return an empty `venueId` and none `accessibility` options if no venues are available', () => {
      const venues: VenueListItemResponseModel[] = []

      const initialValuesResult = getInitialValuesFromVenues(
        venues,
        isNewOfferCreationFlowFeatureActive
      )

      expect(initialValuesResult.venueId).toBe('')
      expect(initialValuesResult.accessibility).toEqual({
        audio: false,
        visual: false,
        motor: false,
        mental: false,
        none: true,
      })
    })

    it('should return a default `venueId` and its `accessibility` props if only one venue is available', () => {
      const venues = [
        venueListItemFactory({
          id: 789,
          audioDisabilityCompliant: true,
          visualDisabilityCompliant: false,
          motorDisabilityCompliant: true,
          mentalDisabilityCompliant: false,
        }),
      ]

      const initialValuesResult = getInitialValuesFromVenues(
        venues,
        isNewOfferCreationFlowFeatureActive
      )

      expect(initialValuesResult.venueId).toBe('789')
      expect(initialValuesResult.accessibility).toEqual({
        audio: true,
        visual: false,
        motor: true,
        mental: false,
        none: false,
      })
    })
  })
})

describe('getFormReadOnlyFields', () => {
  describe('without Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = false

    it('should disable all fields except venue when an ean search filled the form and offer is not yet created', () => {
      const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES).filter(
        (key) => key !== 'venueId'
      )

      expect(
        getFormReadOnlyFields(null, true, isNewOfferCreationFlowFeatureActive)
      ).toStrictEqual(expectedValues)
    })

    it('should disable all field when offer has been created and was created by ean', () => {
      const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

      expect(
        getFormReadOnlyFields(
          getIndividualOfferFactory({ productId: 1 }),
          true,
          isNewOfferCreationFlowFeatureActive
        )
      ).toStrictEqual(expectedValues)
    })

    it('should not disable fields when there is no offer and no ean search was performed', () => {
      expect(
        getFormReadOnlyFields(null, false, isNewOfferCreationFlowFeatureActive)
      ).toStrictEqual([])
    })

    it('should disable category/subcategory/venue fields when updating a regular offer', () => {
      expect(
        getFormReadOnlyFields(
          getIndividualOfferFactory({}),
          false,
          isNewOfferCreationFlowFeatureActive
        )
      ).toStrictEqual(['categoryId', 'subcategoryId', 'venueId'])
    })

    it('should disable all fields when there offer is rejected or pending', () => {
      const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

      expect(
        getFormReadOnlyFields(
          getIndividualOfferFactory({
            status: OfferStatus.REJECTED,
          }),
          false,
          isNewOfferCreationFlowFeatureActive
        )
      ).toStrictEqual(expectedValues)

      expect(
        getFormReadOnlyFields(
          getIndividualOfferFactory({
            status: OfferStatus.PENDING,
          }),
          false,
          isNewOfferCreationFlowFeatureActive
        )
      ).toStrictEqual(expectedValues)
    })

    it('should disable all fields for provided offers', () => {
      const expectedValues = Object.keys(DEFAULT_DETAILS_FORM_VALUES)

      expect(
        getFormReadOnlyFields(
          getIndividualOfferFactory({
            lastProvider: { name: 'provider' },
          }),
          false,
          isNewOfferCreationFlowFeatureActive
        )
      ).toStrictEqual(expectedValues)
    })
  })

  describe('with Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = true

    it('should include accessibility as read-only when the offer status is pending or rejected', () => {
      const pendingOffer = getIndividualOfferFactory({
        status: OfferStatus.PENDING,
      })
      const rejectedOffer = getIndividualOfferFactory({
        status: OfferStatus.REJECTED,
      })

      let isProductBased = false

      expect(
        getFormReadOnlyFields(
          pendingOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).toContain('accessibility')
      expect(
        getFormReadOnlyFields(
          rejectedOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).toContain('accessibility')

      isProductBased = true

      expect(
        getFormReadOnlyFields(
          pendingOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).toContain('accessibility')
      expect(
        getFormReadOnlyFields(
          rejectedOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).toContain('accessibility')
    })

    it('should exclude accessibility for all other cases', () => {
      const nullOffer = null
      const synchronizedOffer = getIndividualOfferFactory({
        lastProvider: getOfferLastProvider(),
      })

      let isProductBased = false

      expect(
        getFormReadOnlyFields(
          nullOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).not.toContain('accessibility')
      expect(
        getFormReadOnlyFields(
          synchronizedOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).not.toContain('accessibility')

      isProductBased = true

      expect(
        getFormReadOnlyFields(
          nullOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).not.toContain('accessibility')
      expect(
        getFormReadOnlyFields(
          synchronizedOffer,
          isProductBased,
          isNewOfferCreationFlowFeatureActive
        )
      ).not.toContain('accessibility')
    })
  })
})

describe('getAccessibilityFormValuesFromOffer', () => {
  it('should coerce all flags to false and set none as true when flags are all false, null or undefined', () => {
    const offer = getIndividualOfferFactory({
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
