import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { GET_COLLECTIVE_FAVORITES } from 'commons/config/swrQueryKeys'
import { defaultCollectiveTemplateOffer } from 'commons/utils/factories/adageFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'

import { OffersFavorites } from '../OffersFavorites'

const mockOffer: CollectiveOfferTemplateResponseModel = {
  ...defaultCollectiveTemplateOffer,
  isFavorite: true,
}

const mockMutate = vi.fn()
vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: vi.fn(() => ({
    mutate: mockMutate,
  })),
}))

const renderAdageFavoritesOffers = (
  user: AuthenticatedResponse,
  features?: string[]
) => {
  renderWithProviders(
    <Routes>
      <Route path="/adage-iframe/recherche" element={<h1>Accueil</h1>} />
      <Route
        path="/adage-iframe/mes-favoris"
        element={
          <AdageUserContextProvider adageUser={user}>
            <OffersFavorites />
          </AdageUserContextProvider>
        }
      />
    </Routes>,
    { initialRouterEntries: ['/adage-iframe/mes-favoris'], features: features }
  )
}

describe('OffersFavorites', () => {
  const user = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
  }

  beforeEach(() => {
    vi.spyOn(apiAdage, 'getCollectiveFavorites').mockResolvedValue({
      favoritesTemplate: [],
    })
  })

  it('should render favorites title', async () => {
    renderAdageFavoritesOffers(user)

    await waitFor(() =>
      expect(screen.queryAllByTestId('spinner')).toHaveLength(0)
    )

    expect(
      screen.getByRole('heading', { name: 'Mes Favoris' })
    ).toBeInTheDocument()
  })

  it('should display no results message whenever favorites list is empty', async () => {
    renderAdageFavoritesOffers(user)

    await waitFor(() =>
      expect(screen.queryAllByTestId('spinner')).toHaveLength(0)
    )

    expect(
      screen.getByText(
        'Explorez le catalogue et ajoutez les offres en favori pour les retrouver facilement !'
      )
    ).toBeInTheDocument()
  })

  it('should display the list of favorites', async () => {
    vi.spyOn(apiAdage, 'getCollectiveFavorites').mockResolvedValueOnce({
      favoritesTemplate: [mockOffer],
    })

    renderAdageFavoritesOffers(user)

    await waitFor(() =>
      expect(screen.queryAllByTestId('spinner')).toHaveLength(0)
    )

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')

    expect(listItemsInOffer).toHaveLength(1)
  })

  it('should redirect to main adage page when clicking the catalogue button', async () => {
    vi.spyOn(apiAdage, 'getCollectiveFavorites').mockResolvedValueOnce({
      favoritesTemplate: [],
    })

    renderAdageFavoritesOffers(user)

    await waitFor(() =>
      expect(screen.queryAllByTestId('spinner')).toHaveLength(0)
    )

    await userEvent.click(screen.getByText('Explorer le catalogue'))

    expect(screen.getByRole('heading', { name: 'Accueil' })).toBeInTheDocument()
  })

  it('should show an offer card', async () => {
    vi.spyOn(apiAdage, 'getCollectiveFavorites').mockResolvedValueOnce({
      favoritesTemplate: [mockOffer],
    })

    renderAdageFavoritesOffers(user)

    await waitFor(() =>
      expect(screen.queryAllByTestId('spinner')).toHaveLength(0)
    )

    expect(
      screen.getByRole('link', { name: mockOffer.name })
    ).toBeInTheDocument()
  })

  it('should reload favorites when favorite is removed', async () => {
    vi.spyOn(apiAdage, 'getCollectiveFavorites').mockResolvedValue({
      favoritesTemplate: [mockOffer],
    })
    vi.spyOn(apiAdage, 'deleteFavoriteForCollectiveOfferTemplate').mockResolvedValue()

    renderAdageFavoritesOffers(user)

    await userEvent.click(
      await screen.findByRole('button', { name: 'Supprimer des favoris' })
    )

    expect(mockMutate).toHaveBeenNthCalledWith(
      1,
      [GET_COLLECTIVE_FAVORITES],
      { favoritesTemplate: [] },
      {
        revalidate: false,
      }
    )
  })
})
