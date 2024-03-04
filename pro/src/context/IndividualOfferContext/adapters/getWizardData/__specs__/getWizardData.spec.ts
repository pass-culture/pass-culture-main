import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import {
  categoryFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'

import { getWizardData } from '../getWizardData'

const venue1: VenueListItemResponseModel = venueListItemFactory({
  id: 2,
  isVirtual: false,
  managingOffererId: 3,
  name: 'mon lieu',
  offererName: 'ma structure',
})

const venue2: VenueListItemResponseModel = venueListItemFactory({
  id: 3,
  isVirtual: false,
  managingOffererId: 4,
  name: 'mon lieu 3',
  offererName: 'ma structure',
})

const offererName1 = {
  id: 68,
  name: 'une structure 1',
}

const offererName2 = {
  id: 79,
  name: 'une structure 2',
}

describe('getWizardData', () => {
  it('should return empty data when user is admin and offerer not specified', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [categoryFactory({ id: 'A', proLabel: 'catégorie 1' })],
      subcategories: [
        subcategoryFactory({
          id: '1',
          proLabel: 'sous-catégorie 1',
        }),
      ],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({ venues: [venue1] })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [offererName1],
    })

    const result = await getWizardData({
      offerer: undefined,
      queryOffererId: undefined,
      isAdmin: true,
    })

    expect(result).toStrictEqual({
      isOk: true,
      message: null,
      payload: {
        categoriesData: {
          categories: [],
          subCategories: [],
        },
        offererNames: [],
        venueList: [],
      },
    })
  })

  it('should return all offerers and venue list when user is not admin and offerer not given', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [venue1],
    })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [offererName1, offererName2],
    })

    const result = await getWizardData({
      offerer: { id: 47, name: 'test' },
      queryOffererId: '666',
      isAdmin: false,
    })

    expect(result).toStrictEqual({
      isOk: true,
      message: null,
      payload: {
        categoriesData: {
          categories: [],
          subCategories: [],
        },
        offererNames: [
          {
            id: 68,
            name: 'une structure 1',
          },
          {
            id: 79,
            name: 'une structure 2',
          },
        ],
        venueList: [
          expect.objectContaining({
            hasCreatedOffer: true,
            hasMissingReimbursementPoint: false,
            id: 2,
            isVirtual: false,
            managingOffererId: 3,
            name: 'mon lieu',
            venueTypeCode: 'Autre',
          }),
        ],
      },
    })
    expect(api.getVenues).toHaveBeenCalledWith(null, true, undefined)
    expect(api.listOfferersNames).toHaveBeenCalledWith(null, null, undefined)
  })

  it('should return all offerers and venue list when user is admin and offerer not given', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [categoryFactory({ id: 'A', proLabel: 'catégorie 1' })],
      subcategories: [
        subcategoryFactory({
          id: '1',
          proLabel: 'sous-catégorie 1',
          appLabel: 'app label',
          isDigitalDeposit: true,
        }),
      ],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({ venues: [venue1] })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [offererName1],
    })

    const result = await getWizardData({
      offerer: undefined,
      queryOffererId: '666',
      isAdmin: true,
    })

    expect(result).toStrictEqual({
      isOk: true,
      message: null,
      payload: {
        categoriesData: {
          categories: [
            {
              id: 'A',
              isSelectable: true,
              proLabel: 'catégorie 1',
            },
          ],
          subCategories: [
            {
              appLabel: 'app label',
              canExpire: true,
              canBeDuo: false,
              canBeEducational: false,
              canBeWithdrawable: false,
              categoryId: 'A',
              conditionalFields: [],
              id: '1',
              isDigitalDeposit: true,
              isEvent: false,
              isPhysicalDeposit: true,
              isSelectable: true,
              onlineOfflinePlatform: 'ONLINE',
              proLabel: 'sous-catégorie 1',
              reimbursementRule: 'STANDARD',
            },
          ],
        },
        offererNames: [
          {
            id: 68,
            name: 'une structure 1',
          },
        ],
        venueList: [
          expect.objectContaining({
            hasCreatedOffer: true,
            hasMissingReimbursementPoint: false,
            id: 2,
            isVirtual: false,
            managingOffererId: 3,
            name: 'mon lieu',
            venueTypeCode: 'Autre',
          }),
        ],
      },
    })
    expect(api.getVenues).toHaveBeenCalledWith(null, true, 666)
    expect(api.listOfferersNames).toHaveBeenCalledWith(null, null, 666)
  })

  it('should return given offerer and venue list when user is admin and offerer was given', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [venue1],
    })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [offererName1, offererName2],
    })

    const result = await getWizardData({
      offerer: { id: 47, name: 'structure test' },
      queryOffererId: '18',
      isAdmin: true,
    })

    expect(result).toStrictEqual({
      isOk: true,
      message: null,
      payload: {
        categoriesData: {
          categories: [],
          subCategories: [],
        },
        offererNames: [
          {
            id: 47,
            name: 'structure test',
          },
        ],
        venueList: [
          expect.objectContaining({
            hasCreatedOffer: true,
            hasMissingReimbursementPoint: false,
            id: 2,
            isVirtual: false,
            managingOffererId: 3,
            name: 'mon lieu',
            venueTypeCode: 'Autre',
          }),
        ],
      },
    })
    expect(api.listOfferersNames).not.toHaveBeenCalled()
  })

  it('should return all venues and all offerers when user is not admin', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [venue1, venue2],
    })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [offererName1, offererName2],
    })

    const result = await getWizardData({
      offerer: { id: 47, name: 'test' },
      queryOffererId: '1',
      isAdmin: false,
    })

    expect(result).toStrictEqual({
      isOk: true,
      message: null,
      payload: {
        categoriesData: {
          categories: [],
          subCategories: [],
        },
        offererNames: [
          {
            id: 68,
            name: 'une structure 1',
          },
          {
            id: 79,
            name: 'une structure 2',
          },
        ],
        venueList: [
          expect.objectContaining({
            hasCreatedOffer: true,
            hasMissingReimbursementPoint: false,
            id: 2,
            isVirtual: false,
            managingOffererId: 3,
            name: 'mon lieu',
            venueTypeCode: 'Autre',
          }),
          expect.objectContaining({
            hasCreatedOffer: true,
            hasMissingReimbursementPoint: false,
            id: 3,
            isVirtual: false,
            managingOffererId: 4,
            name: 'mon lieu 3',
            venueTypeCode: 'Autre',
          }),
        ],
      },
    })
  })

  it('should return failure response when categories call fail', async () => {
    vi.spyOn(api, 'getCategories').mockRejectedValueOnce({})
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [venue1, venue2],
    })

    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [offererName1],
    })

    const result = await getWizardData({
      offerer: undefined,
      queryOffererId: undefined,
      isAdmin: false,
    })

    expect(result).toStrictEqual({
      isOk: false,
      message:
        'Nous avons rencontré un problème lors de la récupération des données.',
      payload: null,
    })
  })

  it('should return failure response when venue call fail', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getVenues').mockRejectedValueOnce({})
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [offererName1],
    })

    const result = await getWizardData({
      offerer: { id: 47, name: 'test' },
      queryOffererId: '1',
      isAdmin: false,
    })

    expect(result).toStrictEqual({
      isOk: false,
      message:
        'Nous avons rencontré un problème lors de la récupération des données.',
      payload: null,
    })
  })

  it('should return failure response when offerer name call fail', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [venue1, venue2],
    })

    vi.spyOn(api, 'listOfferersNames').mockRejectedValueOnce({})

    const result = await getWizardData({
      offerer: { id: 47, name: 'test' },
      queryOffererId: '1',
      isAdmin: false,
    })

    expect(result).toStrictEqual({
      isOk: false,
      message:
        'Nous avons rencontré un problème lors de la récupération des données.',
      payload: null,
    })
  })
})
