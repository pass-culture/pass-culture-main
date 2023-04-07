import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import * as pcapi from 'repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import VenueProvidersManager from '../../index'

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    createVenueProvider: jest.fn(),
    listVenueProviders: jest.fn(),
  },
}))

const renderVenueProvidersManager = async props => {
  renderWithProviders(
    <>
      <VenueProvidersManager {...props} />
      <Notification />
    </>
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

describe('src | StocksProviderForm', () => {
  let props
  let provider
  const venueId = 1
  const providerId = 2
  const venueProviderId = 3

  beforeEach(async () => {
    const venue = {
      id: 'AE',
      nonHumanizedId: venueId,
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
      departementCode: '30',
    }

    props = {
      venue,
    }

    api.listVenueProviders.mockResolvedValue({ venue_providers: [] })
    provider = {
      id: providerId,
      name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
    }
    pcapi.loadProviders.mockResolvedValue([provider])

    await renderVenueProvidersManager(props)
  })

  const renderStocksProviderForm = async () => {
    const importOffersButton = screen.getByText('Synchroniser des offres')
    await userEvent.click(importOffersButton)
    const providersSelect = screen.getByRole('combobox')
    await userEvent.selectOptions(providersSelect, provider.id.toString())
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
      api.createVenueProvider.mockReturnValue(new Promise(() => {}))
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await userEvent.click(submitButton)

      // then
      expect(
        screen.getByText(
          'Certains ouvrages seront exclus de la synchronisation automatique.'
        )
      ).toBeInTheDocument()

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmImportButton)

      expect(
        screen.getByText('Vérification de votre rattachement')
      ).toBeInTheDocument()
      expect(api.createVenueProvider).toHaveBeenCalledWith({
        providerId: provider.id,
        venueId: props.venue.nonHumanizedId,
        venueIdAtOfferProvider: props.venue.siret,
      })
    })

    it('should remove the spinner and display a success notification when venue provider was correctly saved', async () => {
      // given
      const createdVenueProvider = {
        id: venueProviderId,
        provider,
        providerId: provider.id,
        venueId: props.venue.nonHumanizedId,
        venueIdAtOfferProvider: props.venue.siret,
        lastSyncDate: '2018-01-01T00:00:00Z',
        nOffers: 0,
      }
      api.createVenueProvider.mockResolvedValue(createdVenueProvider)
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await userEvent.click(submitButton)

      // then
      expect(
        screen.getByText(
          'Certains ouvrages seront exclus de la synchronisation automatique.'
        )
      ).toBeInTheDocument()

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmImportButton)

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
      const apiError = { provider: ['error message'] }
      api.createVenueProvider.mockRejectedValue(
        new ApiError({}, { body: apiError, status: 400 }, '')
      )
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await userEvent.click(submitButton)

      // then
      expect(
        screen.getByText(
          'Certains ouvrages seront exclus de la synchronisation automatique.'
        )
      ).toBeInTheDocument()

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmImportButton)

      const errorNotification = await screen.findByText(apiError.provider[0])
      expect(errorNotification).toBeInTheDocument()
      const providersSelect = screen.queryByRole('combobox')
      expect(providersSelect).not.toBeInTheDocument()
    })
  })
})
