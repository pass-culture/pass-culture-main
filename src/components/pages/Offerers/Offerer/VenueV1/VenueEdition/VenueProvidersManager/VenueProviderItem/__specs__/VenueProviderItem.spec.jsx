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
  let titeliveVenueProvider
  let allocineVenueProvider

  beforeEach(async () => {
    const venue = {
      id: 'venueId',
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
      departementCode: '75',
    }
    titeliveVenueProvider = {
      id: 'venueProviderId',
      isActive: true,
      lastSyncDate: '2018-01-01T00:00:00Z',
      nOffers: 42,
      provider: {
        name: 'TiteLive',
      },
      venueId: venue.id,
      venueIdAtOfferProvider: 'venueIdAtOfferProvider',
    }
    allocineVenueProvider = {
      id: 'venueProviderId',
      isActive: true,
      isDuo: true,
      lastSyncDate: '2018-01-01T00:00:00Z',
      nOffers: 35,
      price: 10.1,
      provider: {
        name: 'Allociné',
      },
      quantity: 30,
      venueId: venue.id,
      venueIdAtOfferProvider: 'venueIdAtOfferProvider',
    }

    props = {
      venue,
    }

    pcapi.loadVenueProviders.mockResolvedValue([titeliveVenueProvider])
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
    titeliveVenueProvider.lastSyncDate = null

    // when
    await renderVenueProvidersManager(props)

    // then
    const importMessage = screen.getByText(
      'Importation en cours. Cette étape peut durer plusieurs dizaines de minutes. Vous pouvez fermer votre navigateur et revenir plus tard.'
    )
    expect(importMessage).toBeInTheDocument()
    const numberOfOffersLabel = screen.queryByText(`${titeliveVenueProvider.nOffers} offres`)
    expect(numberOfOffersLabel).not.toBeInTheDocument()
  })

  it('should show venue id at offer provider when provided', async () => {
    // when
    await renderVenueProvidersManager(props)

    // then
    const venueIdAtOfferProvider = queryByTextTrimHtml(
      screen,
      `Compte : ${titeliveVenueProvider.venueIdAtOfferProvider}`
    )
    expect(venueIdAtOfferProvider).toBeInTheDocument()
  })

  it('should show the number of offers when data of provider were already synced and offers are provided', async () => {
    // when
    await renderVenueProvidersManager(props)

    // then
    const numberOfOffersLabel = screen.getByText(`${titeliveVenueProvider.nOffers} offres`)
    expect(numberOfOffersLabel).toBeInTheDocument()
  })

  it('should render zero offers label when data of provider were already synced and no offers', async () => {
    // given
    titeliveVenueProvider.nOffers = 0

    // when
    await renderVenueProvidersManager(props)

    // then
    const numberOfOffersLabel = screen.getByText(`0 offre`)
    expect(numberOfOffersLabel).toBeInTheDocument()
  })

  it('should show synchronization modalities when venue provider is allocine', async () => {
    // given
    pcapi.loadVenueProviders.mockResolvedValue([allocineVenueProvider])

    // when
    await renderVenueProvidersManager(props)

    // then
    const price = queryByTextTrimHtml(screen, `Prix de vente/place : 10,10`)
    expect(price).toBeInTheDocument()
    const quantity = queryByTextTrimHtml(
      screen,
      `Nombre de places/séance : ${allocineVenueProvider.quantity}`
    )
    expect(quantity).toBeInTheDocument()
    const isDuo = queryByTextTrimHtml(
      screen,
      `Accepter les offres DUO : ${allocineVenueProvider.isDuo ? 'Oui' : 'Non'}`
    )
    expect(isDuo).toBeInTheDocument()
  })

  it('should show the last synchronization date', async () => {
    // given
    pcapi.loadVenueProviders.mockResolvedValue([allocineVenueProvider])

    // when
    await renderVenueProvidersManager(props)
    const lastSyncDate = screen.getByTestId('last-sync-date')

    // then
    /*eslint-disable-next-line no-irregular-whitespace*/
    expect(lastSyncDate.textContent).toMatchInlineSnapshot(`" 01/01/2018 à 01:00"`)
  })
})
