import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'pages/AdageIframe/app/providers'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AppLayout } from '../AppLayout'

const user = {
  role: AdageFrontRoles.REDACTOR,
}

jest.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: jest.fn().mockResolvedValue({
      categories: [
        { id: 'CINEMA', proLabel: 'Cinéma' },
        { id: 'MUSEE', proLabel: 'Musée' },
      ],
      subcategories: [
        {
          id: 'CINE_PLEIN_AIR',
          proLabel: 'Cinéma plein air',
          categoryId: 'CINEMA',
        },
        {
          id: 'EVENEMENT_CINE',
          proLabel: 'Évènement cinéma',
          categoryId: 'CINEMA',
        },
        {
          id: 'VISITE_GUIDEE',
          proLabel: 'Visite guidée',
          categoryId: 'MUSEE',
        },
        {
          id: 'VISITE',
          proLabel: 'Visite',
          categoryId: 'MUSEE',
        },
      ],
    }),
    getVenueById: jest.fn(),
    authenticate: jest.fn(),
    getVenueBySiret: jest.fn(),
    logSearchButtonClick: jest.fn(),
    logCatalogView: jest.fn(),
    getCollectiveOffer: jest.fn(),
  },
}))

jest.mock('react-instantsearch-dom', () => {
  return {
    ...jest.requireActual('react-instantsearch-dom'),
    Configure: jest.fn(() => <div />),
    connectStats: jest.fn(Component => (props: any) => (
      <Component
        {...props}
        areHitsSorted={false}
        nbHits={0}
        nbSortedHits={0}
        processingTimeMS={0}
      />
    )),
  }
})

jest.mock('utils/config', () => ({
  ALGOLIA_API_KEY: 'adage-api-key',
  ALGOLIA_APP_ID: '1',
  ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
}))

jest.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn(),
  getFeatures: jest.fn(),
}))

const renderAppLayout = (initialRoute = '/') => {
  renderWithProviders(
    <FiltersContextProvider>
      <AlgoliaQueryContextProvider>
        <AppLayout
          user={user}
          removeVenueFilter={jest.fn()}
          venueFilter={null}
        />
      </AlgoliaQueryContextProvider>
    </FiltersContextProvider>,

    { initialRouterEntries: [initialRoute] }
  )
}

describe('AppLayout', () => {
  it('should render new header if FF is active', async () => {
    renderAppLayout()
    waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Pour mon établissement' })
    ).toBeInTheDocument()
  })

  it('should display offers for my institution when url match', async () => {
    renderAppLayout('/mon-etablissement')

    expect(
      screen.getByText('Offres pour mon établissement')
    ).toBeInTheDocument()
  })
})
