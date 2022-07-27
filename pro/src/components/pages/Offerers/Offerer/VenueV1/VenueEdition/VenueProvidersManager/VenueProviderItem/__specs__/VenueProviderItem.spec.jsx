import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import { getProviderInfo } from 'components/pages/Offers/domain/getProviderInfo'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import VenueProvidersManager from '../../VenueProvidersManager'

jest.mock('repository/pcapi/pcapi', () => ({
  createVenueProvider: jest.fn(),
  loadProviders: jest.fn(),
  loadVenueProviders: jest.fn(),
}))

const renderVenueProvidersManager = props =>
  render(
    <Provider store={configureTestStore()}>
      <MemoryRouter>
        <VenueProvidersManager {...props} />
        <NotificationContainer />
      </MemoryRouter>
    </Provider>
  )

describe('src | components | pages | Venue | VenueProvidersManager | VenueProviderItem', () => {
  let props
  let titeliveProvider
  let titeliveProviderDisplayName
  let titeliveVenueProvider

  beforeEach(async () => {
    const venue = {
      id: 'venueId',
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
      departementCode: '75',
    }
    titeliveProvider = {
      id: 'AA',
      name: 'TiteLive',
    }
    titeliveVenueProvider = {
      id: 'venueProviderId',
      isActive: true,
      lastSyncDate: '2018-01-01T00:00:00Z',
      nOffers: 42,
      providerId: titeliveProvider.id,
      provider: titeliveProvider,
      venueId: venue.id,
      venueIdAtOfferProvider: 'venueIdAtOfferProvider',
    }
    titeliveProviderDisplayName = getProviderInfo(titeliveProvider.name).name

    props = {
      venue,
    }

    pcapi.loadVenueProviders.mockResolvedValue([titeliveVenueProvider])
    pcapi.loadProviders.mockResolvedValue([titeliveProvider])
  })

  afterEach(() => {
    jest.resetAllMocks()
  })

  it('should render provider name and logo', async () => {
    // when
    renderVenueProvidersManager(props)
    const venueProviderItemTitle = await screen.findByText(
      titeliveProviderDisplayName
    )

    // then
    expect(venueProviderItemTitle).toBeInTheDocument()
    const providerLogo = screen.getAllByRole('img')[0]
    expect(providerLogo).toHaveAttribute(
      'src',
      expect.stringContaining('logo-titeLive.svg')
    )
  })

  it('should display import message when venue provider is not synced yet', async () => {
    // given
    titeliveVenueProvider.lastSyncDate = null

    // when
    renderVenueProvidersManager(props)
    await screen.findByText(titeliveProviderDisplayName)

    // then
    const importMessage = screen.getByText(
      'Importation en cours. Cette étape peut durer plusieurs dizaines de minutes. Vous pouvez fermer votre navigateur et revenir plus tard.'
    )
    expect(importMessage).toBeInTheDocument()
    const numberOfOffersLabel = screen.queryByText(
      `${titeliveVenueProvider.nOffers} offres`
    )
    expect(numberOfOffersLabel).not.toBeInTheDocument()
  })

  it('should show venue id at offer provider when provided', async () => {
    // when
    renderVenueProvidersManager(props)
    await screen.findByText(titeliveProviderDisplayName)

    // then
    const venueIdAtOfferProvider = queryByTextTrimHtml(
      screen,
      `Compte : ${titeliveVenueProvider.venueIdAtOfferProvider}`
    )
    expect(venueIdAtOfferProvider).toBeInTheDocument()
  })

  it('should show the number of offers when data of provider were already synced and offers are provided', async () => {
    // when
    renderVenueProvidersManager(props)
    await screen.findByText(titeliveProviderDisplayName)

    // then
    const numberOfOffersLabel = screen.getByText(
      `${titeliveVenueProvider.nOffers} offres`
    )
    expect(numberOfOffersLabel).toBeInTheDocument()
  })

  it('should render zero offers label when data of provider were already synced and no offers', async () => {
    // given
    titeliveVenueProvider.nOffers = 0

    // when
    renderVenueProvidersManager(props)
    await screen.findByText(titeliveProviderDisplayName)

    // then
    const numberOfOffersLabel = screen.getByText(`0 offre`)
    expect(numberOfOffersLabel).toBeInTheDocument()
  })

  it('should show the last synchronization date', async () => {
    // given
    pcapi.loadVenueProviders.mockResolvedValue([titeliveVenueProvider])

    // when
    renderVenueProvidersManager(props)
    await screen.findByText(titeliveProviderDisplayName)
    const lastSyncDate = screen.getByTestId('last-sync-date')

    // then
    expect(lastSyncDate.textContent).toMatchInlineSnapshot(
      /*eslint-disable-next-line no-irregular-whitespace*/
      `" 01/01/2018 à 01:00"`
    )
  })
})
