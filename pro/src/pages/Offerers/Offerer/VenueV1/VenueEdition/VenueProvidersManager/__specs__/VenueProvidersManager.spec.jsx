import {
  screen,
  within,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import * as pcapi from 'repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DEFAULT_PROVIDER_OPTION } from '../utils/_constants'
import VenueProvidersManager from '../VenueProvidersManager'

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    deleteVenueProvider: jest.fn(),
    updateVenueProvider: jest.fn(),
    listVenueProviders: jest.fn(),
  },
}))

const renderVenueProvidersManager = async props => {
  renderWithProviders(<VenueProvidersManager {...props} />)

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

describe('src | VenueProvidersManager', () => {
  let props
  let providers
  let venueProviders
  const venueId = 1
  const providerId = 2
  const otherProviderId = 3
  const venueProviderId = 4

  beforeEach(() => {
    const venue = {
      id: 'venueId',
      nonHumanizedId: venueId,
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
      departementCode: '30',
      managingOfferer: {
        nonHumanizedId: 17,
      },
    }

    props = {
      venue,
    }

    providers = [
      { id: providerId, name: 'Cinema provider' },
      { id: otherProviderId, name: 'Movies provider' },
    ]
    venueProviders = []
    pcapi.loadProviders.mockResolvedValue(providers)
    api.listVenueProviders.mockResolvedValue({
      venue_providers: venueProviders,
    })
  })

  it('should retrieve providers and venue providers when component is mounted', async () => {
    // when
    await renderVenueProvidersManager(props)

    // then
    expect(pcapi.loadProviders).toHaveBeenCalledTimes(1)
    expect(api.listVenueProviders).toHaveBeenCalledTimes(1)
  })

  describe('when all providers are disabled for pro', () => {
    it('should display provider section if venue already have one', async () => {
      // Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'TiteLive' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      pcapi.loadProviders.mockResolvedValue([])
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })

      // When
      await renderVenueProvidersManager(props)

      // Then
      expect(screen.queryByText('Importer des offres')).not.toBeInTheDocument()
    })
  })

  describe('when venue has providers synchronized', () => {
    it('should display the list of synchronized providers', async () => {
      // given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 0,
          provider: { id: providerId, name: 'FNAC' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })

      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.getByText('Fnac')).toBeInTheDocument()
      expect(
        screen.queryByText(DEFAULT_PROVIDER_OPTION.displayName)
      ).not.toBeInTheDocument()
    })

    it('should display synchronization activated status when venue provider isActive', async () => {
      // given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 0,
          provider: { id: providerId, name: 'Allocine' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isActive: true,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })

      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.getByText('Synchronisation activée')).toBeInTheDocument()
    })

    it('should display synchronization inactive status when venue provider is not active', async () => {
      // given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 0,
          provider: { id: providerId, name: 'Allocine' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isActive: false,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })

      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.getByText('Synchronisation en pause')).toBeInTheDocument()
    })

    it('should not show import button', async () => {
      // Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'TiteLive' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })

      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.queryByText('Importer des offres')).not.toBeInTheDocument()
    })

    it('should display delete synchronisation button', async () => {
      //Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'TiteLive' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })
      api.deleteVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)

      // Then
      const deleteVenueProviderButton = screen.queryByText('Supprimer')
      expect(deleteVenueProviderButton).toBeInTheDocument()

      // When
      await userEvent.click(deleteVenueProviderButton)
      expect(
        screen.queryByText(
          'Voulez-vous supprimer la synchronisation de vos offres ?'
        )
      ).toBeInTheDocument()
      const confirmDeleteButton = screen.queryByText(
        'Supprimer la synchronisation'
      )
      expect(confirmDeleteButton).toBeInTheDocument()
      await userEvent.click(confirmDeleteButton)

      // Then
      expect(api.deleteVenueProvider).toHaveBeenCalledTimes(1)
    })

    it('should display synchronization parameters when has Allociné provider', async () => {
      // Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'Allociné' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isDuo: true,
          price: 5,
          quantity: 20,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })

      // When
      await renderVenueProvidersManager(props)

      // Then
      expect(
        await screen.findByText('Paramètres des offres synchronisées')
      ).toBeInTheDocument()

      expect(screen.getByText('Prix de vente/place :')).toBeInTheDocument()
      expect(screen.getByText('5,00 €')).toBeInTheDocument()

      expect(screen.getByText('Nombre de places/séance :')).toBeInTheDocument()
      expect(screen.getByText('20')).toBeInTheDocument()

      expect(screen.getByText('Accepter les offres DUO :')).toBeInTheDocument()
      expect(screen.getByText('Oui')).toBeInTheDocument()
    })

    it('should be possible to edit parameters when has Allociné provider', async () => {
      // Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'Allociné' },
          providerId: providerId,
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isDuo: true,
          price: 5,
          quantity: 20,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })
      api.updateVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)
      const editParametersButton = screen.getByText('Modifier les paramètres', {
        selector: 'button',
      })
      await userEvent.click(editParametersButton)

      // Then
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      await userEvent.clear(priceField)
      await userEvent.type(priceField, '10')
      const saveEditionButton = screen.getByText('Modifier', {
        selector: 'button',
      })
      await userEvent.click(saveEditionButton)

      expect(api.updateVenueProvider).toBeCalledWith({
        isDuo: true,
        price: 10,
        providerId: providerId,
        quantity: 20,
        venueId: props.venue.nonHumanizedId,
      })
    })

    it('should be possible to edit parameters when has cinema provider', async () => {
      // Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'ciné office' },
          providerId: providerId,
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isDuo: false,
          isActive: true,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })
      api.updateVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)
      const editParametersButton = screen.getByText('Modifier les paramètres', {
        selector: 'button',
      })
      await userEvent.click(editParametersButton)

      // Then
      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )
      await userEvent.click(isDuoCheckbox)
      const saveEditionButton = screen.getByText('Modifier', {
        selector: 'button',
      })

      await userEvent.click(saveEditionButton)

      expect(api.updateVenueProvider).toBeCalledWith({
        isDuo: true,
        venueId: venueId,
        providerId: providerId,
        isActive: true,
      })
    })

    it('should display synchronization parameters when has Ciné office provider', async () => {
      // Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'ciné office' },
          providerId: providerId,
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isDuo: false,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })
      api.updateVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)

      // Then
      expect(screen.getByText('Accepter les offres DUO :')).toBeInTheDocument()
      expect(screen.getByText('Non')).toBeInTheDocument()
    })

    it('should display pause synchronisation button when venueProvider isActive', async () => {
      //Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'TiteLive' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isActive: true,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })
      api.updateVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)

      // Then
      const pauseVenueProviderButton = screen.queryByText('Mettre en pause')
      expect(pauseVenueProviderButton).toBeInTheDocument()

      // When
      await userEvent.click(pauseVenueProviderButton)

      expect(
        screen.queryByText(
          'Voulez-vous mettre en pause la synchronisation de vos offres ?'
        )
      ).toBeInTheDocument()
      const confirmPauseButton = screen.queryByText(
        'Mettre en pause la synchronisation'
      )
      expect(confirmPauseButton).toBeInTheDocument()
      await userEvent.click(confirmPauseButton)

      // Then
      expect(api.updateVenueProvider).toHaveBeenCalledTimes(1)
    })

    it('should display reactivate synchronisation button when venueProvider is not active', async () => {
      //Given
      venueProviders = [
        {
          id: venueProviderId,
          nOffers: 1,
          provider: { id: providerId, name: 'TiteLive' },
          venueId: props.venue.nonHumanizedId,
          lastSyncDate: '2018-01-01T10:00:00',
          isActive: false,
        },
      ]
      api.listVenueProviders.mockResolvedValue({
        venue_providers: venueProviders,
      })
      api.updateVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)

      // Then
      const reactivateVenueProviderButton = screen.queryByText('Réactiver')
      expect(reactivateVenueProviderButton).toBeInTheDocument()

      // When
      await userEvent.click(reactivateVenueProviderButton)
      expect(
        screen.queryByText(
          'Vous êtes sur le point de réactiver la synchronisation de vos offres.'
        )
      ).toBeInTheDocument()
      const confirmPauseButton = screen.queryByText(
        'Réactiver la synchronisation'
      )
      expect(confirmPauseButton).toBeInTheDocument()
      await userEvent.click(confirmPauseButton)

      // Then
      expect(api.updateVenueProvider).toHaveBeenCalledTimes(1)
    })
  })

  describe('when venue has no providers synchronized', () => {
    it('should not show import button when no providers are given', async () => {
      // given
      providers = []
      pcapi.loadProviders.mockResolvedValue(providers)

      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.queryByText('Importer des offres')).not.toBeInTheDocument()
    })

    it('should show import button when at least one provider is given', async () => {
      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.getByText('Synchroniser des offres')).toBeInTheDocument()
    })

    it('should display a select input to choose a provider on import button click', async () => {
      // given
      await renderVenueProvidersManager(props)
      const importOffersButton = screen.getByText('Synchroniser des offres')

      // when
      await userEvent.click(importOffersButton)

      // then
      const providersSelect = screen.getByRole('combobox')
      expect(providersSelect).toBeInTheDocument()
      expect(providersSelect).toHaveDisplayValue('Choix de la source')
      const providersOptions = within(providersSelect).getAllByRole('option')
      expect(providersOptions[1]).toHaveTextContent(providers[0].name)
      expect(providersOptions[2]).toHaveTextContent(providers[1].name)
    })

    it('should not display the stock form when no provider is selected', async () => {
      // given
      await renderVenueProvidersManager(props)
      const importOffersButton = screen.getByText('Synchroniser des offres')

      // when
      await userEvent.click(importOffersButton)

      // then
      expect(screen.queryByText('Compte')).not.toBeInTheDocument()
      expect(screen.queryByText(props.venue.siret)).not.toBeInTheDocument()
    })

    describe('when selecting a provider', () => {
      it('should display the allocine form when the user choose Allocine onChange', async () => {
        // given
        providers = [
          {
            id: providerId,
            name: 'Allociné',
            lastSyncDate: '2020-01-01T10:00:00',
          },
        ]
        pcapi.loadProviders.mockResolvedValue(providers)
        await renderVenueProvidersManager(props)
        const importOffersButton = screen.getByText('Synchroniser des offres')
        await userEvent.click(importOffersButton)
        const providersSelect = screen.getByRole('combobox')

        // when
        await userEvent.selectOptions(
          providersSelect,
          providers[0].id.toString()
        )

        // then
        expect(screen.getByText('Prix de vente/place')).toBeInTheDocument()
        expect(screen.getByText('Nombre de places/séance')).toBeInTheDocument()
        expect(
          screen.getByText('Accepter les réservations DUO')
        ).toBeInTheDocument()
      })

      it('should display the stock form when the user choose another provider than Allociné', async () => {
        // given
        providers = [
          {
            id: providerId,
            name: 'My little provider',
            hasOffererProvider: false,
          },
        ]
        pcapi.loadProviders.mockResolvedValue(providers)
        await renderVenueProvidersManager(props)
        const importOffersButton = screen.getByText('Synchroniser des offres')
        await userEvent.click(importOffersButton)
        const providersSelect = screen.getByRole('combobox')

        // when
        await userEvent.selectOptions(
          providersSelect,
          providers[0].id.toString()
        )

        // then
        expect(screen.getByText('Compte')).toBeInTheDocument()
        expect(screen.getByText(props.venue.siret)).toBeInTheDocument()
      })
    })
  })
})
