import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import * as pcapi from 'repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import VenueProvidersManager from '../../VenueProvidersManager'

jest.mock('repository/pcapi/pcapi', () => ({
  loadProviders: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    createVenueProvider: jest.fn(),
    updateVenueProvider: jest.fn(),
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

describe('components | CinemaProviderForm', () => {
  let props
  let provider
  let createdVenueProvider

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

    api.listVenueProviders.mockResolvedValue({ venue_providers: [] })

    provider = { id: 'providerId', name: 'Ciné Office' }
    pcapi.loadProviders.mockResolvedValue([provider])
  })

  const renderCinemaProviderForm = async () => {
    await renderVenueProvidersManager(props)

    const importOffersButton = screen.getByText('Synchroniser des offres')
    await userEvent.click(importOffersButton)
    const providersSelect = screen.getByRole('combobox')
    await userEvent.selectOptions(providersSelect, provider.id)
  }

  describe('import form cinema provider for the first time', () => {
    beforeEach(async () => {
      createdVenueProvider = {
        id: 'venueProviderId',
        provider,
        providerId: provider.id,
        venueId: props.venue.id,
        venueIdAtOfferProvider: props.venue.siret,
        lastSyncDate: '2018-01-01T00:00:00Z',
        nOffers: 0,
      }
      api.createVenueProvider.mockResolvedValue(createdVenueProvider)
    })

    it('should display the isDuo checkbox checked by default', async () => {
      // when
      await renderCinemaProviderForm()

      // then
      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )
      expect(isDuoCheckbox).toBeInTheDocument()
      expect(isDuoCheckbox).toBeChecked()
    })

    it('should display import button', async () => {
      // when
      await renderCinemaProviderForm()

      // then
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      expect(offerImportButton).toBeInTheDocument()
      expect(offerImportButton).toHaveAttribute('type', 'submit')
    })

    it('should display a success notification when venue provider was correctly saved', async () => {
      // given
      await renderCinemaProviderForm()
      const offersImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      // when
      await userEvent.click(offersImportButton)

      // then
      const successNotification = await screen.findByText(
        'La synchronisation a bien été initiée.'
      )

      expect(successNotification).toBeInTheDocument()
    })

    it('should display an error notification if there is something wrong with the server', async () => {
      // given
      const apiError = { global: ['Le prix ne peut pas être négatif'] }
      api.createVenueProvider.mockRejectedValue(
        new ApiError({}, { body: apiError, status: 400 }, '')
      )
      await renderCinemaProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      // when
      await userEvent.click(offerImportButton)

      // then
      const errorNotification = await screen.findByText(apiError.global[0])
      expect(errorNotification).toBeInTheDocument()
    })
  })

  describe('edit existing cinema provider', () => {
    let cinemaProvider

    beforeEach(async () => {
      cinemaProvider = {
        id: 'venueProviderId',
        provider,
        providerId: provider.id,
        venueId: props.venue.id,
        venueIdAtOfferProvider: props.venue.siret,
        lastSyncDate: '2018-01-01T00:00:00Z',
        nOffers: 0,
      }

      api.listVenueProviders.mockResolvedValue({
        venue_providers: [cinemaProvider],
      })
    })

    const renderCinemaProviderForm = async () => {
      await renderVenueProvidersManager(props)

      const editProvider = screen.getByText('Modifier les paramètres')
      await userEvent.click(editProvider)
    }

    it('should display modify and cancel button', async () => {
      // when
      await renderCinemaProviderForm()

      // then
      const saveEditionProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      expect(saveEditionProvider).toBeInTheDocument()
      const cancelEditionProvider = screen.getByRole('button', {
        name: 'Annuler',
      })
      expect(cancelEditionProvider).toBeInTheDocument()
    })

    it('should show existing parameters', async () => {
      // given
      cinemaProvider = {
        ...cinemaProvider,
        isDuo: false,
      }
      api.listVenueProviders.mockResolvedValue({
        venue_providers: [cinemaProvider],
      })

      // when
      await renderCinemaProviderForm()

      // then
      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )
      expect(isDuoCheckbox).not.toBeChecked()
    })

    it('should display a success notification when venue provider was correctly updated', async () => {
      // given
      cinemaProvider = {
        ...cinemaProvider,
        isDuo: false,
      }
      api.listVenueProviders.mockResolvedValue({
        venue_providers: [cinemaProvider],
      })
      const editedCinemaProvider = {
        ...cinemaProvider,
        isDuo: true,
      }
      api.updateVenueProvider.mockResolvedValue(editedCinemaProvider)

      await renderCinemaProviderForm()
      const saveEditionProvider = screen.getByRole('button', {
        name: 'Modifier',
      })

      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )

      await userEvent.click(isDuoCheckbox)

      // when
      await userEvent.click(saveEditionProvider)

      // then
      const successNotification = await screen.findByText(
        "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
      )
      expect(successNotification).toBeInTheDocument()
    })
  })
})
