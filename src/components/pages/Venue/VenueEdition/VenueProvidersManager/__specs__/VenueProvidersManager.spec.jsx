import '@testing-library/jest-dom'
import { act, fireEvent, render, screen, within } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import { DEFAULT_PROVIDER_OPTION } from '../utils/providerOptions'
import VenueProvidersManagerContainer from '../VenueProvidersManagerContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
  loadVenueProviders: jest.fn(),
}))

const renderVenueProvidersManagerContainer = async props => {
  await act(async () => {
    await render(
      <Provider store={configureTestStore()}>
        <MemoryRouter>
          <VenueProvidersManagerContainer {...props} />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('src | VenueProvidersManager', () => {
  let props
  let providers
  let venueProviders

  beforeEach(() => {
    const venue = {
      id: 'venueId',
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
    }

    props = {
      venue,
    }

    providers = [
      { id: 'providerId1', requireProviderIdentifier: true, name: 'Cinema provider' },
      { id: 'providerId2', requireProviderIdentifier: true, name: 'Movies provider' },
    ]
    venueProviders = []
    pcapi.loadProviders.mockResolvedValue(providers)
    pcapi.loadVenueProviders.mockResolvedValue(venueProviders)
  })

  afterEach(() => {
    pcapi.loadProviders.mockClear()
    pcapi.loadVenueProviders.mockClear()
  })

  it('should retrieve providers and venue providers when component is mounted', async () => {
    // when
    await renderVenueProvidersManagerContainer(props)

    // then
    expect(pcapi.loadProviders).toHaveBeenCalledTimes(1)
    expect(pcapi.loadVenueProviders).toHaveBeenCalledTimes(1)
  })

  describe('when venue has providers synchronized', () => {
    it('should display the list of synchronized providers', async () => {
      // given
      venueProviders = [
        { id: 'AD', provider: { id: 'providerId', name: 'FNAC' }, venueId: props.venue.id },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)

      // when
      await renderVenueProvidersManagerContainer(props)

      // then
      expect(screen.getByText('Fnac')).toBeInTheDocument()
      expect(screen.queryByText(DEFAULT_PROVIDER_OPTION.name)).not.toBeInTheDocument()
    })

    it('should not show import button', async () => {
      // Given
      venueProviders = [
        { id: 'AD', provider: { id: 'providerId', name: 'TiteLive' }, venueId: props.venue.id },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)

      // when
      await renderVenueProvidersManagerContainer(props)

      // then
      expect(screen.queryByText('Importer des offres')).not.toBeInTheDocument()
    })
  })

  describe('when venue has no providers synchronized', () => {
    it('should not show import button when no providers are given', async () => {
      // given
      providers = []
      pcapi.loadProviders.mockResolvedValue(providers)

      // when
      await renderVenueProvidersManagerContainer(props)

      // then
      expect(screen.queryByText('Importer des offres')).not.toBeInTheDocument()
    })

    it('should show import button when at least one provider is given', async () => {
      // when
      await renderVenueProvidersManagerContainer(props)

      // then
      expect(screen.getByText('Importer des offres')).toBeInTheDocument()
    })

    it('should display a select input to choose a provider on import button click', async () => {
      // given
      await renderVenueProvidersManagerContainer(props)
      const importOffersButton = screen.getByText('Importer des offres')

      // when
      fireEvent.click(importOffersButton)

      // then
      const providersSelect = screen.getByRole('combobox')
      expect(providersSelect).toBeInTheDocument()
      expect(providersSelect).toHaveDisplayValue('Choix de la source')
      const providersOptions = within(providersSelect).getAllByRole('option')
      expect(providersOptions[1]).toHaveTextContent(providers[0].name)
      expect(providersOptions[2]).toHaveTextContent(providers[1].name)
    })

    describe('when selecting a provider', () => {
      it('should display the allocine form when the user choose Allocine onChange', async () => {
        // given
        providers = [{ id: 'providerId', name: 'Allociné', lastSyncDate: '2020-01-01' }]
        pcapi.loadProviders.mockResolvedValue(providers)
        await renderVenueProvidersManagerContainer(props)
        const importOffersButton = screen.getByText('Importer des offres')
        fireEvent.click(importOffersButton)
        const providersSelect = screen.getByRole('combobox')

        // when
        fireEvent.change(providersSelect, { target: { value: providers[0].id } })

        // then
        expect(screen.getByText('Prix de vente/place')).toBeInTheDocument()
        expect(screen.getByText('Nombre de places/séance')).toBeInTheDocument()
        expect(screen.getByText('Accepter les réservations DUO')).toBeInTheDocument()
      })

      it('should display the stock form when the user choose another provider than Allociné', async () => {
        // given
        providers = [
          { id: 'providerId', name: 'TiteLive Stocks (Epagine / Place des libraires.com)' },
        ]
        pcapi.loadProviders.mockResolvedValue(providers)
        await renderVenueProvidersManagerContainer(props)
        const importOffersButton = screen.getByText('Importer des offres')
        fireEvent.click(importOffersButton)
        const providersSelect = screen.getByRole('combobox')

        // when
        fireEvent.change(providersSelect, { target: { value: providers[0].id } })

        // then
        expect(screen.getByText('Compte')).toBeInTheDocument()
        expect(screen.getByText(props.venue.siret)).toBeInTheDocument()
      })
    })
  })
})
