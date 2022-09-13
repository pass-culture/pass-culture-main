import '@testing-library/jest-dom'

import { act, fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import ReactTooltip from 'react-tooltip'

import Notification from 'components/layout/Notification/Notification'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import VenueProvidersManager from '../../VenueProvidersManager'

jest.mock('repository/pcapi/pcapi', () => ({
  createVenueProvider: jest.fn(),
  editVenueProvider: jest.fn(),
  loadProviders: jest.fn(),
  loadVenueProviders: jest.fn(),
}))

const renderVenueProvidersManager = async props => {
  await act(async () => {
    await render(
      <Provider store={configureTestStore()}>
        <MemoryRouter>
          <VenueProvidersManager {...props} />
          <Notification />
          <ReactTooltip html />
        </MemoryRouter>
      </Provider>
    )
  })
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

    pcapi.loadVenueProviders.mockResolvedValue([])

    provider = { id: 'providerId', name: 'Ciné Office' }
    pcapi.loadProviders.mockResolvedValue([provider])
  })

  const renderCinemaProviderForm = async () => {
    await renderVenueProvidersManager(props)

    const importOffersButton = screen.getByText('Synchroniser des offres')
    fireEvent.click(importOffersButton)
    const providersSelect = screen.getByRole('combobox')
    fireEvent.change(providersSelect, { target: { value: provider.id } })
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
      }
      pcapi.createVenueProvider.mockResolvedValue(createdVenueProvider)
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
      fireEvent.click(offersImportButton)

      // then
      const successNotification = await screen.findByText(
        'La synchronisation a bien été initiée.'
      )

      expect(successNotification).toBeInTheDocument()
    })

    it('should display an error notification if there is something wrong with the server', async () => {
      // given
      const apiError = {
        errors: { global: ['Le prix ne peut pas être négatif'] },
        status: 400,
      }
      pcapi.createVenueProvider.mockRejectedValue(apiError)
      await renderCinemaProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      // when
      await fireEvent.click(offerImportButton)

      // then
      const errorNotification = await screen.findByText(
        apiError.errors.global[0]
      )
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
      }

      pcapi.loadVenueProviders.mockResolvedValue([cinemaProvider])
    })

    const renderCinemaProviderForm = async () => {
      await renderVenueProvidersManager(props)

      const editProvider = screen.getByText('Modifier les paramètres')
      fireEvent.click(editProvider)
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
      pcapi.loadVenueProviders.mockResolvedValue([cinemaProvider])

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
      pcapi.loadVenueProviders.mockResolvedValue([cinemaProvider])
      const editedCinemaProvider = {
        ...cinemaProvider,
        isDuo: true,
      }
      pcapi.editVenueProvider.mockResolvedValue(editedCinemaProvider)

      await renderCinemaProviderForm()
      const saveEditionProvider = screen.getByRole('button', {
        name: 'Modifier',
      })

      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )

      fireEvent.change(isDuoCheckbox, { target: { value: true } })

      // when
      fireEvent.click(saveEditionProvider)

      // then
      const successNotification = await screen.findByText(
        'Les modifications ont bien été importées et s’appliqueront aux nouvelles séances créées.'
      )
      expect(successNotification).toBeInTheDocument()
    })
  })
})
