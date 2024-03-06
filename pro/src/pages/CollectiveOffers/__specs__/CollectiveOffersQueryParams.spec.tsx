import { Store } from '@reduxjs/toolkit'
import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { CollectiveOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOffers } from '../CollectiveOffers'

//FIX ME : extract inital values and constant to reduce code duplication with CollectiveOffers.spec.tsx

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useNavigate: vi.fn(),
}))

const renderOffers = async (
  storeOverrides: Store,
  filters: Partial<SearchFiltersParams> = DEFAULT_SEARCH_FILTERS
) => {
  const route = computeCollectiveOffersUrl(filters)
  renderWithProviders(
    <router.Routes>
      <router.Route path="/offres/collectives" element={<CollectiveOffers />} />

      <router.Route
        path="/offres"
        element={
          <>
            <h1>Offres individuelles</h1>
          </>
        }
      ></router.Route>
    </router.Routes>,
    {
      storeOverrides,
      initialRouterEntries: [route],
    }
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

  return {
    history,
  }
}

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

vi.mock('repository/venuesService', async () => ({
  ...((await vi.importActual('repository/venuesService')) ?? {}),
}))

describe('route CollectiveOffers', () => {
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
  }
  let store: any
  let offersRecap: CollectiveOfferResponseModel[]
  const mockNavigate = vi.fn()

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
    }
    offersRecap = [collectiveOfferFactory()]
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    vi.spyOn(api, 'getVenues').mockResolvedValue(
      // @ts-expect-error FIX ME
      { venues: proVenues }
    )
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      const offersRecap = Array.from({ length: 11 }, () =>
        collectiveOfferFactory()
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers(store)
      const nextPageIcon = screen.getByRole('button', { name: 'Page suivante' })

      await userEvent.click(nextPageIcon)

      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives?page=2')
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      await renderOffers(store)

      await userEvent.type(
        screen.getByPlaceholderText('Rechercher par nom d’offre'),
        'AnyWord'
      )
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?nom-ou-isbn=AnyWord'
      )
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      await renderOffers(store)

      await userEvent.clear(
        screen.getByPlaceholderText('Rechercher par nom d’offre')
      )
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives')
    })

    it('should have venue value when user filters by venue', async () => {
      await renderOffers(store)
      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByLabelText('Lieu')

      await userEvent.selectOptions(venueSelect, firstVenueOption)
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        `/offres/collectives?lieu=${proVenues[0].id}`
      )
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers(store)
      const firstTypeOption = screen.getByRole('option', {
        name: 'Concert',
      })
      const typeSelect = screen.getByDisplayValue('Tous')
      // When
      await userEvent.selectOptions(typeSelect, firstTypeOption)
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?format=Concert'
      )
    })

    it('should have status value when user filters by status', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
        collectiveOfferFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: OfferStatus.ACTIVE,
          },
          // @ts-expect-error collectiveOfferFactory is not typed and null throws an error but is accepted by the function
          null
        ),
      ])
      await renderOffers(store)
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut Afficher ou masquer le filtre par statut',
        })
      )
      await userEvent.click(screen.getByLabelText('Réservée'))

      await userEvent.click(screen.getByText('Appliquer'))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?statut=reservee'
      )
    })

    it('should have status value be removed when user ask for all status', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
        collectiveOfferFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: OfferStatus.ACTIVE,
          },
          // @ts-expect-error collectiveOfferFactory is not typed and null throws an error but is accepted by the function
          null
        ),
      ])
      await renderOffers(store)
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut Afficher ou masquer le filtre par statut',
        })
      )
      await userEvent.click(screen.getByLabelText('Toutes'))

      await userEvent.click(screen.getByText('Appliquer'))

      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives')
    })

    it('should have offerer filter when user filters by offerer', async () => {
      const filters = { offererId: 'A4' }
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        name: 'La structure',
      })

      await renderOffers(store, filters)

      const offererFilter = screen.getByText('La structure')
      expect(offererFilter).toBeInTheDocument()
    })

    it('should have offerer value be removed when user removes offerer filter', async () => {
      const filters = { offererId: 'A4' }
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        name: 'La structure',
      })
      await renderOffers(store, filters)

      await userEvent.click(screen.getByTestId('remove-offerer-filter'))

      expect(screen.queryByText('La structure')).not.toBeInTheDocument()
    })
  })

  describe('page navigation', () => {
    it('should redirect to individual offers when user clicks on individual offers link', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
      await renderOffers(store)
      screen.getByText('Rechercher')
      const individualAudienceLink = screen.getByText('Offres individuelles', {
        selector: 'span',
      })

      await userEvent.click(individualAudienceLink)

      expect(screen.getByRole('heading', { name: 'Offres individuelles' }))
    })
  })
})
