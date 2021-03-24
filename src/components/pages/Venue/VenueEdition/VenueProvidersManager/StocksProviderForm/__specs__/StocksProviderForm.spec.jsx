import '@testing-library/jest-dom'
import { act, fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import NotificationV1Container from 'components/layout/NotificationV1/NotificationV1Container'
import * as providersApi from 'repository/pcapi/providersApi'
import { configureTestStore } from 'store/testUtils'

import VenueProvidersManagerContainer from '../../VenueProvidersManagerContainer'


jest.mock('repository/pcapi/providersApi', () => ({
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
          <NotificationV1Container />
        </MemoryRouter>
      </Provider>
    )
  })
}

const renderStocksProviderForm = async () => {
  const importOffersButton = screen.getByText('Importer des offres')
  fireEvent.click(importOffersButton)
  const providersSelect = screen.getByRole('combobox')
  fireEvent.change(providersSelect, { target: { value: 'titelive' } })
}

describe('src | StocksProviderForm', () => {
  let props
  let provider

  beforeEach(async () => {
    const venue = {
      id: 'AB',
      managingOffererId: 'BA',
      name: 'Le lieu',
      siret: '12345678901234',
    }

    props = {
      venue,
    }

    providersApi.loadVenueProviders.mockResolvedValue([])
    provider = { id: 'titelive', name: 'TiteLive Stocks (Epagine / Place des libraires.com)' }
    providersApi.loadProviders.mockResolvedValue([provider])

    await renderVenueProvidersManager(props)
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('should display an import button and the venue siret as provider identifier', async () => {
    // when
    await renderStocksProviderForm()

    // then
    expect(screen.queryByRole('button', { name: 'Importer' })).toBeInTheDocument()
    expect(screen.queryByText('Compte')).toBeInTheDocument()
    expect(screen.queryByText('12345678901234')).toBeInTheDocument()
  })

  describe('on form submit', () => {
    it('should display the spinner while waiting for server response', async () => {
      // given
      providersApi.createVenueProvider.mockReturnValue(new Promise(() => {}))
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await fireEvent.click(submitButton)

      // then
      expect(screen.getByText('Vérification de votre rattachement')).toBeInTheDocument()
      expect(providersApi.createVenueProvider).toHaveBeenCalledWith({
        providerId: provider.id,
        venueId: props.venue.id,
        venueIdAtOfferProvider: props.venue.siret,
      })
    })

    it('should remove the spinner when the server has responded', async () => {
      // given
      const createdVenueProvider = {
        id: 'AQ',
        provider,
        providerId: provider.id,
        venueId: props.venue.id,
        venueIdAtOfferProvider: props.venue.siret,
      }
      providersApi.createVenueProvider.mockResolvedValue(createdVenueProvider)
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await fireEvent.click(submitButton)

      // then
      expect(screen.queryByText('Vérification de votre rattachement')).not.toBeInTheDocument()
    })

    it('should display a notification and unselect provider if there is something wrong with the server', async () => {
      // given
      const apiError = {
        errors: { provider: ['error message'] },
        status: 400,
      }
      providersApi.createVenueProvider.mockRejectedValue(apiError)
      await renderStocksProviderForm()
      const submitButton = screen.getByRole('button', { name: 'Importer' })

      // when
      await fireEvent.click(submitButton)

      // then
      const errorNotification = await screen.findByText(apiError.errors.provider[0])
      expect(errorNotification).toBeInTheDocument()
      const providersSelect = screen.queryByRole('combobox')
      expect(providersSelect).not.toBeInTheDocument()
    })
  })
})
