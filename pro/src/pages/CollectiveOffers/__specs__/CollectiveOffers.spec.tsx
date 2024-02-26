import { Store } from '@reduxjs/toolkit'
import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { CollectiveOfferResponseModel, OfferStatus } from 'apiClient/v1'
import {
  ALL_VENUES,
  ALL_VENUES_OPTION,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOffers } from '../CollectiveOffers'
import { collectiveOfferFactory } from '../utils/collectiveOffersFactories'

const proVenues = [
  {
    id: 1,
    name: 'Ma venue',
    offererName: 'Mon offerer',
    isVirtual: false,
  },
  {
    id: 2,
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  },
]

const renderOffers = async (
  storeOverrides: Store,
  filters: Partial<SearchFiltersParams> = DEFAULT_SEARCH_FILTERS
) => {
  const route = computeCollectiveOffersUrl(filters)
  renderWithProviders(<CollectiveOffers />, {
    storeOverrides,
    initialRouterEntries: [route],
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

  return {
    history,
  }
}

vi.mock('repository/venuesService', async () => ({
  ...((await vi.importActual('repository/venuesService')) ?? {}),
}))

vi.mock('utils/date', async () => ({
  ...((await vi.importActual('utils/date')) ?? {}),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

vi.mock('hooks/useActiveFeature', () => ({
  __esModule: true,
  default: vi.fn().mockReturnValue(true),
}))

describe('route CollectiveOffers', () => {
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
  }
  let store: any
  let offersRecap: CollectiveOfferResponseModel[]

  beforeEach(() => {
    currentUser = {
      id: 'EY',
      isAdmin: false,
      name: 'Current User',
    }
    store = {
      user: {
        initialized: true,
        currentUser,
      },
      offers: {
        searchFilters: DEFAULT_SEARCH_FILTERS,
      },
    }
    offersRecap = [collectiveOfferFactory()]
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'getVenues').mockResolvedValue(
      // @ts-expect-error FIX ME
      { venues: proVenues }
    )
  })

  describe('render', () => {
    describe('filters', () => {
      describe('status filters', () => {
        it('should filter offers given status filter when clicking on "Appliquer"', async () => {
          await renderOffers(store)
          await userEvent.click(
            screen.getByRole('button', {
              name: 'Statut Afficher ou masquer le filtre par statut',
            })
          )
          await userEvent.click(screen.getByLabelText('Expirée'))

          await userEvent.click(screen.getByText('Appliquer'))

          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            'EXPIRED',
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should indicate that no offers match selected filters', async () => {
          vi.spyOn(api, 'getCollectiveOffers')
            .mockResolvedValueOnce(offersRecap)
            .mockResolvedValueOnce([])
          await renderOffers(store)

          await userEvent.click(
            screen.getByRole('button', {
              name: 'Statut Afficher ou masquer le filtre par statut',
            })
          )
          await userEvent.click(screen.getByLabelText('Expirée'))
          await userEvent.click(screen.getByText('Appliquer'))

          const noOffersForSearchFiltersText = screen.getByText(
            'Aucune offre trouvée pour votre recherche'
          )
          expect(noOffersForSearchFiltersText).toBeInTheDocument()
        })

        it('should not display column titles when no offers are returned', async () => {
          vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

          await renderOffers(store)

          expect(screen.queryByText('Lieu', { selector: 'th' })).toBeNull()
          expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
        })
      })

      describe('when user is admin', () => {
        beforeEach(() => {
          store = {
            user: {
              initialized: true,
              currentUser: { ...currentUser, isAdmin: true },
            },
            offers: {
              searchFilters: DEFAULT_SEARCH_FILTERS,
            },
          }
        })
        describe('status filter can only be used with an offerer or a venue filter for performance reasons', () => {
          it('should reset and disable status filter when venue filter is deselected', async () => {
            const { id: venueId, name: venueName } = proVenues[0]
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
            }
            await renderOffers(store, filters)
            await userEvent.selectOptions(
              screen.getByDisplayValue(venueName),
              ALL_VENUES
            )

            await userEvent.click(screen.getByText('Rechercher'))

            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined
            )
          })

          it('should not reset or disable status filter when venue filter is deselected while offerer filter is applied', async () => {
            const { id: venueId, name: venueName } = proVenues[0]
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
              offererId: 'EF',
            }
            await renderOffers(store, filters)
            await userEvent.selectOptions(
              screen.getByDisplayValue(venueName),
              ALL_VENUES
            )

            await userEvent.click(screen.getByText('Rechercher'))

            expect(
              screen.getByRole('button', {
                name: /Afficher ou masquer le filtre par statut/,
              })
            ).not.toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
              undefined,
              'EF',
              'INACTIVE',
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined
            )
          })

          it('should reset and disable status filter when offerer filter is removed', async () => {
            const offerer = { name: 'La structure', id: 'EF' }
            // @ts-expect-error FIX ME
            vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              offererId: offerer.id,
              status: OfferStatus.INACTIVE,
            }
            await renderOffers(store, filters)

            await userEvent.click(screen.getByTestId('remove-offerer-filter'))

            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined
            )
          })

          it('should not reset or disable status filter when offerer filter is removed while venue filter is applied', async () => {
            const { id: venueId } = proVenues[0]
            const offerer = { name: 'La structure', id: 'EF' }
            // @ts-expect-error FIX ME
            vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
              offererId: offerer.id,
            }
            await renderOffers(store, filters)

            await userEvent.click(screen.getByTestId('remove-offerer-filter'))

            expect(
              screen.getByRole('button', {
                name: /Afficher ou masquer le filtre par statut/,
              })
            ).not.toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
              undefined,
              undefined,
              'INACTIVE',
              venueId.toString(),
              undefined,
              undefined,
              undefined,
              undefined,
              undefined,
              undefined
            )
          })

          it('should enable status filters when venue filter is applied', async () => {
            const filters = { venueId: proVenues[0].id.toString() }

            await renderOffers(store, filters)

            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).not.toBeDisabled()
          })

          it('should enable status filters when offerer filter is applied', async () => {
            const filters = { offererId: 'A4' }

            await renderOffers(store, filters)

            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).not.toBeDisabled()
          })
        })
      })

      describe('on click on search button', () => {
        it('should load offers with written offer name filter', async () => {
          await renderOffers(store)
          await userEvent.type(
            screen.getByPlaceholderText('Rechercher par nom d’offre'),
            'Any word'
          )

          await userEvent.click(screen.getByText('Rechercher'))

          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'Any word',
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should store search value', async () => {
          await renderOffers(store)
          const searchInput = screen.getByPlaceholderText(
            'Rechercher par nom d’offre'
          )

          await userEvent.type(searchInput, 'search string')
          await userEvent.click(screen.getByText('Rechercher'))

          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'search string',
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should load offers with selected venue filter', async () => {
          await renderOffers(store)
          const firstVenueOption = screen.getByRole('option', {
            name: proVenues[0].name,
          })
          const venueSelect = screen.getByLabelText('Lieu')
          await userEvent.selectOptions(venueSelect, firstVenueOption)

          await userEvent.click(screen.getByText('Rechercher'))

          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            undefined,
            undefined,
            undefined,
            proVenues[0].id.toString(),
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should load offers with selected period beginning date', async () => {
          await renderOffers(store)

          await userEvent.type(
            screen.getByLabelText('Début de la période'),
            '2020-12-25'
          )

          await userEvent.click(screen.getByText('Rechercher'))

          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-25',
            undefined,
            undefined,
            undefined
          )
        })

        it('should load offers with selected period ending date', async () => {
          await renderOffers(store)
          await userEvent.type(
            screen.getByLabelText('Fin de la période'),
            '2020-12-27'
          )

          await userEvent.click(screen.getByText('Rechercher'))

          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-27',
            undefined,
            undefined
          )
        })

        it('should load offers with selected offer type', async () => {
          await renderOffers(store)
          const offerTypeSelect = screen.getByLabelText('Type de l’offre')
          await userEvent.selectOptions(offerTypeSelect, 'template')

          await userEvent.click(screen.getByText('Rechercher'))

          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            'template',
            undefined
          )
        })
      })
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      const offers = Array.from({ length: 11 }, () => collectiveOfferFactory())
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)
      await renderOffers(store)
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

      await userEvent.click(nextIcon)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      const offers = Array.from({ length: 11 }, () => collectiveOfferFactory())
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)
      await renderOffers(store)
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

    describe('when 501 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 501 }, () =>
          collectiveOfferFactory()
        )
      })

      it('should have max number page of 50', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)

        await renderOffers(store)

        expect(screen.getByText('Page 1/50')).toBeInTheDocument()
      })

      it('should not display the 501st offer', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
        await renderOffers(store)
        const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

        for (let i = 1; i < 51; i++) {
          await userEvent.click(nextIcon)
        }

        expect(screen.getByLabelText(offersRecap[499].name)).toBeInTheDocument()
        expect(
          screen.queryByText(offersRecap[500].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('should reset filters', () => {
    it('when clicking on "afficher toutes les offres" when no offers are displayed', async () => {
      vi.spyOn(api, 'getCollectiveOffers')
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      await renderOffers(store)

      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

      await userEvent.selectOptions(venueSelect, firstVenueOption)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Rechercher'))

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        undefined,
        undefined,
        undefined,
        proVenues[0].id.toString(),
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )

      screen.getByText('Aucune offre trouvée pour votre recherche')

      await userEvent.click(screen.getByText('Afficher toutes les offres'))

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(3)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        3,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })

    it('when clicking on "Réinitialiser les filtres"', async () => {
      vi.spyOn(api, 'getCollectiveOffers')
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      await renderOffers(store)

      const venueOptionToSelect = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

      await userEvent.selectOptions(venueSelect, venueOptionToSelect)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Rechercher'))
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        undefined,
        undefined,
        undefined,
        proVenues[0].id.toString(),
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Réinitialiser les filtres'))
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(3)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        3,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })
  })
})
