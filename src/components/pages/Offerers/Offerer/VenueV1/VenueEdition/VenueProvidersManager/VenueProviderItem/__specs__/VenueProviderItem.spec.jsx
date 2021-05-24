import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import VenueProvidersManagerContainer from '../../VenueProvidersManagerContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  createVenueProvider: jest.fn(),
  loadProviders: jest.fn(),
  loadVenueProviders: jest.fn(),
}))

const renderVenueProvidersManager = async props => {
  await act(async () => {
    await render(
      <Provider store={configureTestStore()}>
        <MemoryRouter>
          <VenueProvidersManagerContainer {...props} />
          <NotificationContainer />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('src | components | pages | Venue | VenueProvidersManager | VenueProviderItem', () => {
  let props
  let venueProvider

  beforeEach(async () => {
    const venue = {
      id: 'venueId',
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
    }
    venueProvider = {
      id: 'venueProviderId',
      isActive: true,
      lastSyncDate: '2018-01-01T10:00:00',
      nOffers: 42,
      provider: {
        name: 'TiteLive',
      },
      venueId: venue.id,
      venueIdAtOfferProvider: 'venueIdAtOfferProvider',
    }

    props = {
      venue,
    }

    pcapi.loadVenueProviders.mockResolvedValue([venueProvider])
    pcapi.loadProviders.mockResolvedValue([])
  })

  it('should render provider name and logo', async () => {
    // when
    await renderVenueProvidersManager(props)

    // then
    expect(screen.getByText('Tite Live')).toBeInTheDocument()
    const providerLogo = screen.getAllByRole('img')[0]
    expect(providerLogo).toHaveAttribute('src', expect.stringContaining('logo-titeLive.svg'))
  })

  it('should display import message when venue provider is not synced yet', async () => {
    // given
    venueProvider.lastSyncDate = null

    // when
    await renderVenueProvidersManager(props)

    // then
    const importMessage = screen.getByText(
      'Importation en cours. Cette étape peut durer plusieurs dizaines de minutes. Vous pouvez fermer votre navigateur et revenir plus tard.'
    )
    expect(importMessage).toBeInTheDocument()
    const numberOfOffersLabel = screen.queryByText(`${venueProvider.nOffers} offres`)
    expect(numberOfOffersLabel).not.toBeInTheDocument()
  })

  it('should show venue id at offer provider when provided', async () => {
    // when
    await renderVenueProvidersManager(props)

    // then
    const venueIdAtOfferProvider = queryByTextTrimHtml(
      screen,
      `Compte : ${venueProvider.venueIdAtOfferProvider}`
    )
    expect(venueIdAtOfferProvider).toBeInTheDocument()
  })

  it('should show the number of offers when data of provider were already synced and offers are provided', async () => {
    // when
    await renderVenueProvidersManager(props)

    // then
    const numberOfOffersLabel = screen.getByText(`${venueProvider.nOffers} offres`)
    expect(numberOfOffersLabel).toBeInTheDocument()
  })

  it('should render zero offers label when data of provider were already synced and no offers', async () => {
    // given
    venueProvider.nOffers = 0

    // when
    await renderVenueProvidersManager(props)

    // then
    const numberOfOffersLabel = screen.getByText(`0 offre`)
    expect(numberOfOffersLabel).toBeInTheDocument()
  })
})
