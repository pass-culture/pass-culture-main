import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersFavorites } from '../OffersFavorites'

const mockOffer: CollectiveOfferTemplateResponseModel = {
  ...defaultCollectiveTemplateOffer,
}

const renderAdageFavoritesOffers = (user: AuthenticatedResponse) => {
  renderWithProviders(
    <Routes>
      <Route path="/adage-iframe/recherche" element={<h1>Accueil</h1>} />
      <Route
        path="/adage-iframe/mes-favoris"
        element={
          <AdageUserContextProvider adageUser={user}>
            <OffersFavorites></OffersFavorites>
          </AdageUserContextProvider>
        }
      />
    </Routes>,
    { initialRouterEntries: ['/adage-iframe/mes-favoris'] }
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

  it('should render favorites title', async () => {
    renderAdageFavoritesOffers(user)

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(
      screen.getByRole('heading', { name: 'Mes Favoris' })
    ).toBeInTheDocument()
  })

  it('should display no results message whenever favorites list is empty', async () => {
    renderAdageFavoritesOffers(user)

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(
      screen.getByText(
        'Explorez le catalogue et ajoutez les offres en favori pour les retrouver facilement !'
      )
    ).toBeInTheDocument()
  })

  it('should display the list of favorites', async () => {
    vi.spyOn(apiAdage, 'getCollectiveFavorites').mockResolvedValueOnce({
      favoritesOffer: [],
      favoritesTemplate: [mockOffer],
    })

    renderAdageFavoritesOffers(user)

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')

    expect(listItemsInOffer).toHaveLength(1)
  })

  it('should redirect to main adage page when clicking the catalogue button', async () => {
    vi.spyOn(apiAdage, 'getCollectiveFavorites').mockResolvedValueOnce({
      favoritesTemplate: [],
      favoritesOffer: [],
    })

    renderAdageFavoritesOffers(user)

    await waitFor(() =>
      expect(screen.queryByText(/Chargement en cours/)).not.toBeInTheDocument()
    )

    await userEvent.click(screen.getByText('Explorer le catalogue'))

    expect(screen.getByRole('heading', { name: 'Accueil' })).toBeInTheDocument()
  })
})
