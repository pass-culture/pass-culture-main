import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { act, fireEvent, render, screen } from '@testing-library/react'

import { MemoryRouter } from 'react-router'
import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import { Provider } from 'react-redux'
import React from 'react'
import VenueProvidersManager from '../../VenueProvidersManager'
import { configureTestStore } from 'store/testUtils'

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
          <VenueProvidersManager {...props} />
          <NotificationContainer />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('src | StocksProviderForm', () => {
  let props
  let provider

  beforeEach(async () => {
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

    pcapi.loadVenueProviders.mockResolvedValue([])
    provider = {
      id: 'providerId',
      name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
    }
    pcapi.loadProviders.mockResolvedValue([provider])

    await renderVenueProvidersManager(props)
  })

  const renderStocksProviderForm = async () => {
    const importOffersButton = screen.getByText('Synchroniser des offres')
    fireEvent.click(importOffersButton)
    const providersSelect = screen.getByRole('combobox')
    fireEvent.change(providersSelect, { target: { value: provider.id } })
  }

  it('should display an import button and the venue siret as provider identifier', async () => {
    // when
    await renderStocksProviderForm()

    // then
    expect(
      screen.queryByRole('button', { name: 'Importer' })
    ).toBeInTheDocument()
    expect(screen.queryByText('Compte')).toBeInTheDocument()
    expect(screen.queryByText(props.venue.siret)).toBeInTheDocument()
  })

  describe('on form submit', () => {
    it('should display the spinner while waiting for server response', async () => {
      // given
      pcapi.createVenueProvider.mockReturnValue(new Promise(() => {}))
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await fireEvent.click(submitButton)

      // then
      expect(
        screen.getByText(
          'Certains ouvrages seront exclus de la synchronisation automatique.'
        )
      ).toBeInTheDocument()

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await fireEvent.click(confirmImportButton)

      expect(
        screen.getByText('Vérification de votre rattachement')
      ).toBeInTheDocument()
      expect(pcapi.createVenueProvider).toHaveBeenCalledWith({
        providerId: provider.id,
        venueId: props.venue.id,
        venueIdAtOfferProvider: props.venue.siret,
      })
    })

    it('should remove the spinner and display a success notification when venue provider was correctly saved', async () => {
      // given
      const createdVenueProvider = {
        id: 'venueProviderId',
        provider,
        providerId: provider.id,
        venueId: props.venue.id,
        venueIdAtOfferProvider: props.venue.siret,
        lastSyncDate: '2018-01-01T00:00:00Z',
      }
      pcapi.createVenueProvider.mockResolvedValue(createdVenueProvider)
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await fireEvent.click(submitButton)

      // then
      expect(
        screen.getByText(
          'Certains ouvrages seront exclus de la synchronisation automatique.'
        )
      ).toBeInTheDocument()

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await fireEvent.click(confirmImportButton)

      const successNotification = await screen.findByText(
        'La synchronisation a bien été initiée.'
      )
      expect(successNotification).toBeInTheDocument()
      expect(
        screen.queryByText('Vérification de votre rattachement')
      ).not.toBeInTheDocument()
    })

    it('should display a notification and unselect provider if there is something wrong with the server', async () => {
      // given
      const apiError = {
        errors: { provider: ['error message'] },
        status: 400,
      }
      pcapi.createVenueProvider.mockRejectedValue(apiError)
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await fireEvent.click(submitButton)

      // then
      expect(
        screen.getByText(
          'Certains ouvrages seront exclus de la synchronisation automatique.'
        )
      ).toBeInTheDocument()

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await fireEvent.click(confirmImportButton)

      const errorNotification = await screen.findByText(
        apiError.errors.provider[0]
      )
      expect(errorNotification).toBeInTheDocument()
      const providersSelect = screen.queryByRole('combobox')
      expect(providersSelect).not.toBeInTheDocument()
    })
  })
})
