import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import * as pcapi from 'repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import VenueProvidersManager from '../../VenueProvidersManager'

const mockLogEvent = jest.fn()

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
  let providers
  const venueId = 1
  const providerId = 2
  const otherProviderId = 4
  const venueProviderId = 3

  beforeEach(async () => {
    const venue = {
      id: 'AE',
      nonHumanizedId: venueId,
      managingOffererId: 'managingOffererId',
      name: 'Le lieu',
      siret: '12345678901234',
      departementCode: '30',
      managingOfferer: {
        nonHumanizedId: 36,
      },
    }

    props = {
      venue,
    }

    api.listVenueProviders.mockResolvedValue({ venue_providers: [] })
    providers = [
      {
        id: providerId,
        name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
        hasOffererProvider: false,
      },
      {
        id: otherProviderId,
        name: 'Riot records',
        hasOffererProvider: true,
      },
    ]

    pcapi.loadProviders.mockResolvedValue(providers)

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  const openStocksProviderForm = async providerId => {
    const importOffersButton = screen.getByText('Synchroniser des offres')
    await userEvent.click(importOffersButton)
    const providersSelect = screen.getByRole('combobox')
    await userEvent.selectOptions(providersSelect, providerId.toString())
  }

  it('should display an import button and the venue siret as provider identifier', async () => {
    await renderVenueProvidersManager(props)
    // when

    await openStocksProviderForm(providers[0].id)

    // then
    expect(
      screen.queryByRole('button', { name: 'Importer les offres' })
    ).toBeInTheDocument()
    expect(screen.queryByText('Compte')).toBeInTheDocument()
    expect(screen.queryByText(props.venue.siret)).toBeInTheDocument()
  })

  it('should display an import button but no account identifier', async () => {
    await renderVenueProvidersManager(props)

    // when
    await openStocksProviderForm(providers[1].id)

    // then
    expect(
      screen.queryByRole('button', { name: 'Importer les offres' })
    ).toBeInTheDocument()
    expect(screen.queryByText('Compte')).not.toBeInTheDocument()
    expect(screen.queryByText(props.venue.siret)).not.toBeInTheDocument()
  })

  describe('on form submit', () => {
    it('should display the spinner while waiting for server response', async () => {
      // given
      await renderVenueProvidersManager(props)
      api.createVenueProvider.mockReturnValue(new Promise(() => {}))
      await openStocksProviderForm(providers[0].id)
      const submitButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      // when
      await userEvent.click(submitButton)

      // then
      expect(
        screen.getByText('Certaines offres ne seront pas synchronisées')
      ).toBeInTheDocument()

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmImportButton)

      expect(
        screen.getByText('Vérification de votre rattachement')
      ).toBeInTheDocument()
      expect(api.createVenueProvider).toHaveBeenCalledWith({
        providerId: providers[0].id,
        venueId: props.venue.nonHumanizedId,
        venueIdAtOfferProvider: props.venue.siret,
      })
    })

    it('should remove the spinner and display a success notification when venue provider was correctly saved', async () => {
      // given
      const createdVenueProvider = {
        id: venueProviderId,
        provider: providers[0],
        providerId: providers[0].id,
        venueId: props.venue.nonHumanizedId,
        venueIdAtOfferProvider: props.venue.siret,
        lastSyncDate: '2018-01-01T00:00:00Z',
        nOffers: 0,
      }
      api.createVenueProvider.mockResolvedValue(createdVenueProvider)
      await renderVenueProvidersManager(props)

      await openStocksProviderForm(providers[0].id)
      const submitButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      // when
      await userEvent.click(submitButton)

      // then
      expect(
        screen.getByText('Certaines offres ne seront pas synchronisées')
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

    it('should track on import', async () => {
      // given
      const createdVenueProvider = {
        id: venueProviderId,
        provider: providers[0],
        providerId: providers[0].id,
        venueId: props.venue.nonHumanizedId,
        venueIdAtOfferProvider: props.venue.siret,
        lastSyncDate: '2018-01-01T00:00:00Z',
        nOffers: 0,
      }
      api.createVenueProvider.mockResolvedValue(createdVenueProvider)
      await renderVenueProvidersManager(props)

      await openStocksProviderForm(providers[0].id)
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        SynchronizationEvents.CLICKED_SYNCHRONIZE_OFFER,
        {
          offererId: 36,
          venueId: 1,
        }
      )

      const submitButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      await userEvent.click(submitButton)

      expect(mockLogEvent).toHaveBeenCalledTimes(2)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        2,
        SynchronizationEvents.CLICKED_IMPORT,
        {
          offererId: 36,
          venueId: 1,
          providerId: 2,
        }
      )

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmImportButton)

      expect(mockLogEvent).toHaveBeenCalledTimes(3)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        3,
        SynchronizationEvents.CLICKED_VALIDATE_IMPORT,
        {
          offererId: 36,
          venueId: 1,
          providerId: 2,
        }
      )
    })

    it('should display a notification and unselect provider if there is something wrong with the server', async () => {
      // given
      const apiError = { provider: ['error message'] }
      api.createVenueProvider.mockRejectedValue(
        new ApiError({}, { body: apiError, status: 400 }, '')
      )
      await renderVenueProvidersManager(props)

      await openStocksProviderForm(providers[0].id)
      const submitButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      // when
      await userEvent.click(submitButton)

      // then
      expect(
        screen.getByText('Certaines offres ne seront pas synchronisées')
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
