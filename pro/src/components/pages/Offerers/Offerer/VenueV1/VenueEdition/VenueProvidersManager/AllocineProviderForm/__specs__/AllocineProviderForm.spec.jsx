import '@testing-library/jest-dom'

import {
  render,
  screen,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import ReactTooltip from 'react-tooltip'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import Notification from 'components/layout/Notification/Notification'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import VenueProvidersManager from '../../VenueProvidersManager'

jest.mock('repository/pcapi/pcapi', () => ({
  editVenueProvider: jest.fn(),
  loadProviders: jest.fn(),
  loadVenueProviders: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    createVenueProvider: jest.fn(),
  },
}))

const renderVenueProvidersManager = async props => {
  render(
    <Provider store={configureTestStore()}>
      <MemoryRouter>
        <VenueProvidersManager {...props} />
        <Notification />
        <ReactTooltip html />
      </MemoryRouter>
    </Provider>
  )
  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

describe('components | AllocineProviderForm', () => {
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

    provider = { id: 'providerId', name: 'Allociné' }
    pcapi.loadProviders.mockResolvedValue([provider])
  })

  const renderAllocineProviderForm = async () => {
    await renderVenueProvidersManager(props)

    const importOffersButton = screen.getByText('Synchroniser des offres')
    await userEvent.click(importOffersButton)
    const providersSelect = screen.getByRole('combobox')
    await userEvent.selectOptions(providersSelect, provider.id)
  }

  it('should display the price field with minimum value set to 0', async () => {
    // when
    await renderAllocineProviderForm()

    // then
    const priceField = screen.getByLabelText('Prix de vente/place', {
      exact: false,
    })
    expect(priceField).toBeInTheDocument()
    expect(priceField).toHaveAttribute('min', '0')
    expect(priceField).toHaveAttribute('step', '0.01')
  })

  it('should display the quantity field with default value set to Illimité', async () => {
    // when
    await renderAllocineProviderForm()

    // then
    const quantityField = screen.getByLabelText(`Nombre de places/séance`)
    expect(quantityField).toBeInTheDocument()
    expect(quantityField).toHaveAttribute('min', '0')
    expect(quantityField).toHaveAttribute('step', '1')
  })

  describe('import form allocine provider for the first time', () => {
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
      await renderAllocineProviderForm()

      // then
      const isDuoCheckbox = screen.getByLabelText(
        `Accepter les réservations DUO`
      )
      expect(isDuoCheckbox).toBeInTheDocument()
      expect(isDuoCheckbox).toBeChecked()
    })

    it('should display an import button disabled by default', async () => {
      // when
      await renderAllocineProviderForm()

      // then
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      expect(offerImportButton).toBeInTheDocument()
      expect(offerImportButton).toHaveAttribute('type', 'submit')
      expect(offerImportButton).toBeDisabled()
    })

    it('should be able to submit when price field is filled', async () => {
      // given
      await renderAllocineProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      const quantityField = screen.getByLabelText('Nombre de places/séance')
      const isDuoCheckbox = screen.getByLabelText(
        `Accepter les réservations DUO`
      )

      // when
      await userEvent.type(priceField, '10')
      await userEvent.type(quantityField, '5')
      await userEvent.click(isDuoCheckbox)
      await userEvent.click(offerImportButton)

      // then
      expect(api.createVenueProvider).toHaveBeenCalledWith({
        price: 10,
        quantity: 5,
        isDuo: false,
        providerId: provider.id,
        venueId: props.venue.id,
      })
    })

    it('should be able to submit when price field is filled to 0', async () => {
      // given
      await renderAllocineProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })

      // when
      await userEvent.type(priceField, '0')
      await userEvent.click(offerImportButton)

      // then
      expect(api.createVenueProvider).toHaveBeenCalledWith({
        price: 0,
        quantity: undefined,
        isDuo: true,
        providerId: provider.id,
        venueId: props.venue.id,
      })
    })

    it('should be able to submit when price field is filled with a decimal', async () => {
      // given
      await renderAllocineProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })

      // when
      await userEvent.type(priceField, '0.42')
      await userEvent.click(offerImportButton)

      // then
      expect(api.createVenueProvider).toHaveBeenCalledWith({
        price: 0.42,
        quantity: undefined,
        isDuo: true,
        providerId: provider.id,
        venueId: props.venue.id,
      })
    })

    it('should not be able to submit when quantity is filled but price is not', async () => {
      // given
      await renderAllocineProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      const quantityField = screen.getByLabelText('Nombre de places/séance')

      // when
      await userEvent.type(quantityField, '10')
      await userEvent.click(offerImportButton)

      // then
      expect(api.createVenueProvider).toHaveBeenCalledTimes(0)
    })

    it('should display a success notification when venue provider was correctly saved', async () => {
      // given
      await renderAllocineProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      await userEvent.type(priceField, '10')

      // when
      await userEvent.click(offerImportButton)

      // then
      const successNotification = await screen.findByText(
        'La synchronisation a bien été initiée.'
      )
      expect(successNotification).toBeInTheDocument()
    })

    it('should display an error notification if there is something wrong with the server', async () => {
      // given
      const apiError = {
        global: ['Le prix ne peut pas être négatif'],
      }
      api.createVenueProvider.mockRejectedValue(
        new ApiError(
          {},
          {
            body: apiError,
            status: 400,
          },
          ''
        )
      )
      await renderAllocineProviderForm()
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })

      // when
      await userEvent.type(priceField, '-10')
      await userEvent.click(offerImportButton)

      // then
      const errorNotification = await screen.findByText(apiError.global[0])
      expect(errorNotification).toBeInTheDocument()
    })
  })

  describe('edit existing allocine provider', () => {
    let allocineProvider

    beforeEach(async () => {
      allocineProvider = {
        id: 'venueProviderId',
        provider,
        providerId: provider.id,
        venueId: props.venue.id,
        venueIdAtOfferProvider: props.venue.siret,
        lastSyncDate: '2018-01-01T00:00:00Z',
        nOffers: 0,
        price: 0,
        quantity: 0,
        isDuo: true,
      }

      pcapi.loadVenueProviders.mockResolvedValue([allocineProvider])
    })

    const renderAllocineProviderForm = async () => {
      await renderVenueProvidersManager(props)

      const editProvider = screen.getByText('Modifier les paramètres')
      await userEvent.click(editProvider)
    }

    it('should display modify and cancel button', async () => {
      // when
      await renderAllocineProviderForm()

      // then
      const saveEditioProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      expect(saveEditioProvider).toBeInTheDocument()
      const cancelEditionProvider = screen.getByRole('button', {
        name: 'Annuler',
      })
      expect(cancelEditionProvider).toBeInTheDocument()
    })

    it('should show existing parameters', async () => {
      // given
      allocineProvider = {
        ...allocineProvider,
        price: 15,
        quantity: 50,
        isDuo: false,
      }
      pcapi.loadVenueProviders.mockResolvedValue([allocineProvider])

      // when
      await renderAllocineProviderForm()

      // then
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      expect(priceField).toHaveValue(allocineProvider.price)

      const quantityField = screen.getByLabelText('Nombre de places/séance', {
        exact: false,
      })
      expect(quantityField).toHaveValue(allocineProvider.quantity)

      const isDuoField = screen.getByLabelText(
        'Accepter les réservations DUO',
        { exact: false }
      )
      expect(isDuoField).not.toBeChecked()
    })

    it('should not be able to submit when price field is not filled', async () => {
      // given
      allocineProvider = {
        ...allocineProvider,
        price: 15,
        quantity: 50,
        isDuo: false,
      }
      await renderAllocineProviderForm()
      const saveEditioProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })

      // when
      await userEvent.clear(priceField)

      // then
      expect(saveEditioProvider).toBeDisabled()
    })

    it('should be able to submit when price field is filled', async () => {
      // given
      allocineProvider = {
        ...allocineProvider,
        price: 15,
        quantity: 50,
        isDuo: false,
      }
      pcapi.loadVenueProviders.mockResolvedValue([allocineProvider])
      const editedAllocineProvider = {
        ...allocineProvider,
        price: 20,
        quantity: 10,
        isDuo: true,
      }

      pcapi.editVenueProvider.mockResolvedValue(editedAllocineProvider)

      await renderAllocineProviderForm()

      const saveEditioProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      const quantityField = screen.getByLabelText('Nombre de places/séance')
      const isDuoCheckbox = screen.getByLabelText(
        `Accepter les réservations DUO`
      )

      // when
      await userEvent.clear(priceField)
      await userEvent.clear(quantityField)
      await userEvent.type(priceField, `${editedAllocineProvider.price}`)
      await userEvent.type(quantityField, `${editedAllocineProvider.quantity}`)

      await userEvent.click(isDuoCheckbox)
      await userEvent.click(saveEditioProvider)

      // then
      expect(pcapi.editVenueProvider).toHaveBeenCalledWith({
        price: editedAllocineProvider.price,
        quantity: editedAllocineProvider.quantity,
        isDuo: editedAllocineProvider.isDuo,
        providerId: provider.id,
        venueId: props.venue.id,
      })
    })

    it('should not send quantity when it value is removed', async () => {
      // given
      allocineProvider = {
        ...allocineProvider,
        price: 20,
        quantity: 50,
        isDuo: false,
      }
      pcapi.loadVenueProviders.mockResolvedValue([allocineProvider])
      const editedAllocineProvider = {
        ...allocineProvider,
        price: 20,
        quantity: null,
        isDuo: false,
      }

      pcapi.editVenueProvider.mockResolvedValue(editedAllocineProvider)

      await renderAllocineProviderForm()

      const saveEditioProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      const quantityField = screen.getByLabelText('Nombre de places/séance')

      // when
      await userEvent.clear(quantityField)
      await userEvent.click(saveEditioProvider)

      // then
      expect(pcapi.editVenueProvider).toHaveBeenCalledWith({
        price: editedAllocineProvider.price,
        quantity: editedAllocineProvider.quantity,
        isDuo: editedAllocineProvider.isDuo,
        providerId: provider.id,
        venueId: props.venue.id,
      })
    })

    it('should display a success notification when venue provider was correctly updated', async () => {
      // given
      allocineProvider = {
        ...allocineProvider,
        price: 15,
        quantity: 50,
        isDuo: false,
      }
      pcapi.loadVenueProviders.mockResolvedValue([allocineProvider])
      const editedAllocineProvider = {
        ...allocineProvider,
        price: 20,
        quantity: 50,
        isDuo: false,
      }
      pcapi.editVenueProvider.mockResolvedValue(editedAllocineProvider)

      await renderAllocineProviderForm()
      const saveEditioProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })

      await userEvent.type(priceField, '10')

      // when
      await userEvent.click(saveEditioProvider)

      // then
      const successNotification = await screen.findByText(
        'Les modifications ont bien été importées et s’appliqueront aux nouvelles séances créées.'
      )
      expect(successNotification).toBeInTheDocument()
    })

    it('should display an error notification if there is something wrong with the server', async () => {
      // given
      const editedAllocineProvider = {
        ...allocineProvider,
        price: 20,
        quantity: 50,
        isDuo: false,
      }
      pcapi.editVenueProvider.mockResolvedValue(editedAllocineProvider)
      const apiError = {
        errors: { global: ['Le prix ne peut pas être négatif'] },
        status: 400,
      }
      pcapi.editVenueProvider.mockRejectedValue(apiError)
      await renderAllocineProviderForm()
      const saveEditioProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })

      // when
      await userEvent.clear(priceField)
      await userEvent.type(priceField, '-10')
      await userEvent.click(saveEditioProvider)

      // then
      const errorNotification = await screen.findByText(
        apiError.errors.global[0]
      )
      expect(errorNotification).toBeInTheDocument()
    })
  })
})
