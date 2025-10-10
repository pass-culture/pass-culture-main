import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import {
  CollectiveLocationType,
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
  type CollectiveOffersStockResponseModel,
  CollectiveOfferType,
  EacFormat,
  type GetOffererAddressResponseModel,
} from '@/apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { offererAddressFactory } from '@/commons/utils/factories/offererAddressFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffers } from '../CollectiveOffers'

const LABELS = {
  nameSearchInput: /Nom de l’offre/,
}

const stocks: Array<CollectiveOffersStockResponseModel> = [
  {
    startDatetime: String(new Date()),
    hasBookingLimitDatetimePassed: false,
    remainingQuantity: 1,
  },
]

const offersRecap: CollectiveOfferResponseModel[] = [
  collectiveOfferFactory({ stocks }),
]

vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))

vi.mock('@/apiClient/api', () => {
  return {
    api: {
      getCollectiveOffers: vi.fn(),
      getOfferer: vi.fn(),
      listOfferersNames: vi.fn(),
      getOffererAddresses: vi.fn(),
    },
  }
})

const offererAddress: GetOffererAddressResponseModel[] = [
  offererAddressFactory({
    label: 'Label',
  }),
  offererAddressFactory({
    city: 'New York',
  }),
]

const renderOffers = async (
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  features: string[] = []
) => {
  const route = computeCollectiveOffersUrl(filters)
  const user = sharedCurrentUserFactory()
  renderWithProviders(<CollectiveOffers />, {
    user,
    initialRouterEntries: [route],
    features,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: currentOffererFactory(),
    },
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

const offererId = '1'

describe('CollectiveOffers', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
    })
    vi.spyOn(api, 'getOffererAddresses').mockResolvedValue(offererAddress)
  })

  afterEach(() => {
    window.sessionStorage.clear()
  })

  it('should fetch only bookable offers', async () => {
    await renderOffers()

    await waitFor(() => {
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
        offererId,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        CollectiveOfferType.OFFER,
        undefined,
        undefined,
        undefined
      )
    })
  })

  describe('filters', () => {
    describe('status filters', () => {
      it('should filter offers given status filter when clicking on "Appliquer"', async () => {
        await renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Expirée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
            2,
            undefined,
            offererId,
            [CollectiveOfferDisplayedStatus.EXPIRED],
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            undefined,
            undefined
          )
        })
      })

      it('should filter offers given multiple status filter when clicking on "Appliquer"', async () => {
        await renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Expirée'))
        await userEvent.click(screen.getByText('Préréservée'))
        await userEvent.click(screen.getByText('Réservée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
            2,
            undefined,
            offererId,
            [
              CollectiveOfferDisplayedStatus.EXPIRED,
              CollectiveOfferDisplayedStatus.PREBOOKED,
              CollectiveOfferDisplayedStatus.BOOKED,
            ],
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            undefined,
            undefined
          )
        })
      })

      it('should indicate that no offers match selected filters', async () => {
        vi.spyOn(api, 'getCollectiveOffers')
          .mockResolvedValueOnce(offersRecap)
          .mockResolvedValueOnce([])
        await renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Expirée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(
            screen.getByText('Aucune offre trouvée pour votre recherche')
          ).toBeInTheDocument()
        })
      })

      it('should not display column titles when no offers are returned', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

        await renderOffers()

        expect(screen.queryByText('Lieu', { selector: 'th' })).toBeNull()
        expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
      })
    })

    describe('location type filters', () => {
      it('should send locationType ADDRESS and offererAddressId when feature flag is active and an address is selected', async () => {
        await renderOffers(DEFAULT_COLLECTIVE_SEARCH_FILTERS)
        await userEvent.selectOptions(
          screen.getByLabelText('Localisation'),
          offererAddress[0].id.toString()
        )
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            offererId,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            CollectiveLocationType.ADDRESS,
            1
          )
        })
      })

      it('should send locationType TO_BE_DEFINED and offererAddressId undefined when "À déterminer" is selected', async () => {
        await renderOffers(DEFAULT_COLLECTIVE_SEARCH_FILTERS)
        const localisationSelect = await screen.findByLabelText('Localisation')
        await userEvent.selectOptions(
          localisationSelect,
          CollectiveLocationType.TO_BE_DEFINED
        )
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            offererId,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            CollectiveLocationType.TO_BE_DEFINED,
            null
          )
        })
      })

      it('should send locationType SCHOOL and offererAddressId undefined when "En établissement scolaire" is selected', async () => {
        await renderOffers(DEFAULT_COLLECTIVE_SEARCH_FILTERS)
        const localisationSelect = await screen.findByLabelText('Localisation')
        await userEvent.selectOptions(
          localisationSelect,
          CollectiveLocationType.SCHOOL
        )
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            offererId,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            CollectiveLocationType.SCHOOL,
            null
          )
        })
      })

      it('should send locationType and offererAddressId undefined when "all" is selected', async () => {
        await renderOffers(DEFAULT_COLLECTIVE_SEARCH_FILTERS)
        const localisationSelect = await screen.findByLabelText('Localisation')
        await userEvent.selectOptions(localisationSelect, 'all')
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            offererId,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            undefined,
            undefined
          )
        })
      })
    })

    describe('on click on search button', () => {
      it('should load offers with written offer name filter', async () => {
        await renderOffers()

        const searchInput = screen.getByRole('searchbox', {
          name: LABELS.nameSearchInput,
        })

        await userEvent.type(searchInput, 'Any word')

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'Any word',
            offererId,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            undefined,
            undefined
          )
        })
      })

      it('should load offers with selected period beginning date', async () => {
        await renderOffers()

        await userEvent.type(
          screen.getByLabelText('Début de la période'),
          '2020-12-25'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            offererId,
            undefined,
            undefined,
            undefined,
            '2020-12-25',
            undefined,
            CollectiveOfferType.OFFER,
            undefined,
            undefined,
            undefined
          )
        })
      })

      it('should load offers with selected period ending date', async () => {
        await renderOffers()
        await userEvent.type(
          screen.getByLabelText('Fin de la période'),
          '2020-12-27'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            offererId,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-27',
            CollectiveOfferType.OFFER,
            undefined,
            undefined,
            undefined
          )
        })
      })
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferFactory({ stocks })
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)
      await renderOffers()
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

      await userEvent.click(nextIcon)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferFactory({ stocks })
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)
      await renderOffers()
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })
      const previousIcon = screen.getByRole('button', {
        name: 'Page précédente',
      })
      await userEvent.click(nextIcon)

      await userEvent.click(previousIcon)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    describe('when 101 offers are fetched', () => {
      const offersRecap = Array.from({ length: 101 }, () =>
        collectiveOfferFactory({ stocks })
      )

      it('should have max number page of 10', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)

        await renderOffers()

        expect(screen.getByText('Page 1/10')).toBeInTheDocument()
      })

      it('should not display the 101st offer', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
        await renderOffers()
        const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

        for (let i = 1; i < 11; i++) {
          await userEvent.click(nextIcon)
        }

        expect(screen.getByLabelText(offersRecap[99].name)).toBeInTheDocument()
        expect(
          screen.queryByText(offersRecap[100].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('should reset filters', () => {
    it('when clicking on "afficher toutes les offres" when no offers are displayed', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

      const filters = {
        format: EacFormat.ATELIER_DE_PRATIQUE,
      }
      await renderOffers(filters)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        offererId,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        CollectiveOfferType.OFFER,
        'Atelier de pratique',
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Rechercher'))
      await waitFor(() => {
        expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      })
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        offererId,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        CollectiveOfferType.OFFER,
        'Atelier de pratique',
        undefined,
        undefined
      )

      screen.getByText('Aucune offre trouvée pour votre recherche')

      await userEvent.click(screen.getByText('Afficher toutes les offres'))
      await waitFor(() => {
        expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      })
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        undefined,
        offererId,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        CollectiveOfferType.OFFER,
        undefined,
        undefined,
        undefined
      )
    })

    it('when clicking on "Réinitialiser les filtres"  - except nameOrIsbn', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

      const nameOrIsbn = 'Any word'
      await renderOffers({
        nameOrIsbn,
        format: EacFormat.ATELIER_DE_PRATIQUE,
      })

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        1,
        nameOrIsbn,
        offererId,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        CollectiveOfferType.OFFER,
        'Atelier de pratique',
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Réinitialiser les filtres'))
      await waitFor(() => {
        expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      })
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        nameOrIsbn,
        offererId,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        CollectiveOfferType.OFFER,
        undefined,
        undefined,
        undefined
      )
    })
  })

  it('should show draft offers ', async () => {
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
      collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      }),
      collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      }),
    ])
    await renderOffers(DEFAULT_COLLECTIVE_SEARCH_FILTERS)

    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })
})
