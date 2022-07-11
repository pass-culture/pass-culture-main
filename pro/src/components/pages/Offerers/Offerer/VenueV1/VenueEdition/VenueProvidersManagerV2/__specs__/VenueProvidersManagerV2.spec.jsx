import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'
import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { DEFAULT_PROVIDER_OPTION } from '../../VenueProvidersManager/utils/_constants'
import { MemoryRouter } from 'react-router'
import { Provider } from 'react-redux'
import React from 'react'
import VenueProvidersManagerV2 from '../VenueProvidersManagerV2'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
  loadVenueProviders: jest.fn(),
  deleteVenueProvider: jest.fn(),
  editVenueProvider: jest.fn(),
}))

const renderVenueProvidersManager = async props => {
  await act(async () => {
    await render(
      <Provider store={configureTestStore()}>
        <MemoryRouter>
          <VenueProvidersManagerV2 {...props} />
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
      departementCode: '30',
    }

    props = {
      venue,
    }

    providers = [
      { id: 'providerId1', name: 'Cinema provider' },
      { id: 'providerId2', name: 'Movies provider' },
    ]
    venueProviders = []
    pcapi.loadProviders.mockResolvedValue(providers)
    pcapi.loadVenueProviders.mockResolvedValue(venueProviders)
  })

  it('should retrieve providers and venue providers when component is mounted', async () => {
    // when
    await renderVenueProvidersManager(props)

    // then
    expect(pcapi.loadProviders).toHaveBeenCalledTimes(1)
    expect(pcapi.loadVenueProviders).toHaveBeenCalledTimes(1)
  })

  describe('when all providers are disabled for pro', () => {
    it('should display provider section if venue already have one', async () => {
      // Given
      venueProviders = [
        {
          id: 'AD',
          nOffers: 1,
          provider: { id: 'providerId', name: 'TiteLive' },
          venueId: props.venue.id,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      pcapi.loadProviders.mockResolvedValue([])
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)

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
          id: 'AD',
          nOffers: 0,
          provider: { id: 'providerId', name: 'FNAC' },
          venueId: props.venue.id,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)

      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.getByText('Fnac')).toBeInTheDocument()
      expect(
        screen.queryByText(DEFAULT_PROVIDER_OPTION.displayName)
      ).not.toBeInTheDocument()
    })

    it('should not show import button', async () => {
      // Given
      venueProviders = [
        {
          id: 'AD',
          nOffers: 1,
          provider: { id: 'providerId', name: 'TiteLive' },
          venueId: props.venue.id,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)

      // when
      await renderVenueProvidersManager(props)

      // then
      expect(screen.queryByText('Importer des offres')).not.toBeInTheDocument()
    })

    it('should display delete synchronisation button', async () => {
      //Given
      venueProviders = [
        {
          id: 'AD',
          nOffers: 1,
          provider: { id: 'providerId', name: 'TiteLive' },
          venueId: props.venue.id,
          lastSyncDate: '2018-01-01T10:00:00',
        },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)
      pcapi.deleteVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)

      // Then
      const deleteVenueProviderButton = screen.queryByText('Supprimer')
      expect(deleteVenueProviderButton).toBeInTheDocument()

      // When
      fireEvent.click(deleteVenueProviderButton)
      expect(
        screen.queryByText(
          'Voulez-vous supprimer la synchronisation de vos offres ?'
        )
      ).toBeInTheDocument()
      const confirmDeleteButton = screen.queryByText(
        'Supprimer la synchronisation'
      )
      expect(confirmDeleteButton).toBeInTheDocument()
      fireEvent.click(confirmDeleteButton)

      // Then
      expect(pcapi.deleteVenueProvider).toHaveBeenCalledTimes(1)
    })

    it('should display synchronization parameters when has Allociné provider', async () => {
      // Given
      venueProviders = [
        {
          id: 'AD',
          nOffers: 1,
          provider: { id: 'providerId', name: 'Allociné' },
          venueId: props.venue.id,
          lastSyncDate: '2018-01-01T10:00:00',
          isDuo: true,
          price: 5,
          quantity: 20,
        },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)

      // When
      await renderVenueProvidersManager(props)

      // Then
      expect(
        screen.queryByText('Paramètres des offres synchronisées')
      ).toBeInTheDocument()

      const price = queryByTextTrimHtml(screen, 'Prix de vente/place : 5')
      expect(price).toBeInTheDocument()

      const quantity = queryByTextTrimHtml(
        screen,
        'Nombre de places/séances : 20'
      )
      expect(quantity).toBeInTheDocument()

      const isDuo = queryByTextTrimHtml(screen, 'Accepter les offres DUO : Oui')
      expect(isDuo).toBeInTheDocument()
    })

    it('should be possible to edit parameters when has Allociné provider', async () => {
      // Given
      venueProviders = [
        {
          id: 'AD',
          nOffers: 1,
          provider: { id: 'BC', name: 'Allociné' },
          providerId: 'BC',
          venueId: props.venue.id,
          lastSyncDate: '2018-01-01T10:00:00',
          isDuo: true,
          price: 5,
          quantity: 20,
        },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)
      pcapi.editVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)
      const editParametersButton = screen.getByText('Modifier les paramètres', {
        selector: 'button',
      })
      fireEvent.click(editParametersButton)

      // Then
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      fireEvent.change(priceField, { target: { value: 10 } })
      const saveEditionButton = screen.getByText('Modifier', {
        selector: 'button',
      })
      fireEvent.click(saveEditionButton)

      expect(pcapi.editVenueProvider).toBeCalledWith({
        isDuo: true,
        price: 10,
        providerId: 'BC',
        quantity: 20,
        venueId: 'venueId',
      })
    })

    it('should display synchronization parameters when has Ciné office provider', async () => {
      // Given
      venueProviders = [
        {
          id: 'AD',
          nOffers: 1,
          provider: { id: 'BC', name: 'ciné office' },
          providerId: 'BC',
          venueId: props.venue.id,
          lastSyncDate: '2018-01-01T10:00:00',
          isDuo: false,
        },
      ]
      pcapi.loadVenueProviders.mockResolvedValue(venueProviders)
      pcapi.editVenueProvider.mockResolvedValue()

      // When
      await renderVenueProvidersManager(props)

      // Then
      const isDuo = queryByTextTrimHtml(screen, 'Accepter les offres DUO : Non')
      expect(isDuo).toBeInTheDocument()
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
      expect(screen.getByText('Importer des offres')).toBeInTheDocument()
    })

    it('should display a select input to choose a provider on import button click', async () => {
      // given
      await renderVenueProvidersManager(props)
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

    it('should not display the stock form when no provider is selected', async () => {
      // given
      await renderVenueProvidersManager(props)
      const importOffersButton = screen.getByText('Importer des offres')

      // when
      fireEvent.click(importOffersButton)

      // then
      expect(screen.queryByText('Compte')).not.toBeInTheDocument()
      expect(screen.queryByText(props.venue.siret)).not.toBeInTheDocument()
    })

    describe('when selecting a provider', () => {
      it('should display the allocine form when the user choose Allocine onChange', async () => {
        // given
        providers = [
          {
            id: 'providerId',
            name: 'Allociné',
            lastSyncDate: '2020-01-01T10:00:00',
          },
        ]
        pcapi.loadProviders.mockResolvedValue(providers)
        await renderVenueProvidersManager(props)
        const importOffersButton = screen.getByText('Importer des offres')
        fireEvent.click(importOffersButton)
        const providersSelect = screen.getByRole('combobox')

        // when
        fireEvent.change(providersSelect, {
          target: { value: providers[0].id },
        })

        // then
        expect(screen.getByText('Prix de vente/place')).toBeInTheDocument()
        expect(screen.getByText('Nombre de places/séance')).toBeInTheDocument()
        expect(
          screen.getByText('Accepter les réservations DUO')
        ).toBeInTheDocument()
      })

      it('should display the stock form when the user choose another provider than Allociné', async () => {
        // given
        providers = [{ id: 'providerId', name: 'My little provider' }]
        pcapi.loadProviders.mockResolvedValue(providers)
        await renderVenueProvidersManager(props)
        const importOffersButton = screen.getByText('Importer des offres')
        fireEvent.click(importOffersButton)
        const providersSelect = screen.getByRole('combobox')

        // when
        fireEvent.change(providersSelect, {
          target: { value: providers[0].id },
        })

        // then
        expect(screen.getByText('Compte')).toBeInTheDocument()
        expect(screen.getByText(props.venue.siret)).toBeInTheDocument()
      })
    })
  })
})
