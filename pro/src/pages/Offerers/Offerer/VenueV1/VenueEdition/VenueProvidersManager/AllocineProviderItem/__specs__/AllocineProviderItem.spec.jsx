import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import Notification from 'components/Notification/Notification'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import VenueProvidersManager from '../../VenueProvidersManager'

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    createVenueProvider: jest.fn(),
    listVenueProviders: jest.fn(),
  },
}))

const renderVenueProvidersManager = props =>
  render(
    <Provider store={configureTestStore()}>
      <MemoryRouter>
        <VenueProvidersManager {...props} />
        <Notification />
      </MemoryRouter>
    </Provider>
  )

describe('src | components | pages | Venue | VenueProvidersManager | AllocineProviderItem', () => {
  let props
  let allocineProvider
  let allocineVenueProvider

  beforeEach(async () => {
    const venue = {
      id: 'venueId',
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
      departementCode: '75',
    }
    allocineProvider = {
      id: 'CE',
      name: 'Allociné',
    }
    allocineVenueProvider = {
      id: 'venueProviderId',
      isActive: true,
      isDuo: true,
      lastSyncDate: '2018-01-01T00:00:00Z',
      nOffers: 35,
      price: 10.1,
      providerId: allocineProvider.id,
      provider: allocineProvider,
      quantity: 30,
      venueId: venue.id,
      venueIdAtOfferProvider: 'venueIdAtOfferProvider',
    }

    props = {
      venue,
    }

    api.listVenueProviders.mockResolvedValue({
      venue_providers: [allocineVenueProvider],
    })
    pcapi.loadProviders.mockResolvedValue([allocineProvider])
  })

  it('should show synchronization modalities when venue provider is allocine', async () => {
    // given
    api.listVenueProviders.mockResolvedValue({
      venue_providers: [allocineVenueProvider],
    })

    // when
    renderVenueProvidersManager(props)
    await screen.findByText(allocineProvider.name)

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
      // to fix - no-conditional-in-test
      `Accepter les offres DUO : ${allocineVenueProvider.isDuo ? 'Oui' : 'Non'}`
    )
    expect(isDuo).toBeInTheDocument()
  })

  it('should show the last synchronization date', async () => {
    // given
    api.listVenueProviders.mockResolvedValue({
      venue_providers: [allocineVenueProvider],
    })

    // when
    renderVenueProvidersManager(props)
    await screen.findByText(allocineProvider.name)
    const lastSyncDate = screen.getByTestId('last-sync-date')

    // then
    expect(lastSyncDate.textContent).toMatchInlineSnapshot(
      /*eslint-disable-next-line no-irregular-whitespace*/
      `" 01/01/2018 à 01:00"`
    )
  })

  it('should show edit button and open edit dialog when it clicked', async () => {
    // given
    pcapi.loadProviders.mockResolvedValue([allocineVenueProvider])

    // when
    renderVenueProvidersManager(props)
    await screen.findByText(allocineProvider.name)

    // then
    const editAllocineProviderButton = screen.getByText(
      'Modifier les paramètres'
    )
    expect(editAllocineProviderButton).toBeInTheDocument()

    // when
    await userEvent.click(editAllocineProviderButton)

    // then
    expect(
      screen.getByText('Modifier les paramètres de mes offres')
    ).toBeInTheDocument()
  })
})
