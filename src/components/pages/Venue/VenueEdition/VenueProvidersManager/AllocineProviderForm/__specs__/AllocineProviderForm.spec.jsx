import '@testing-library/jest-dom'
import { act, fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import ReactTooltip from 'react-tooltip'

import NotificationV1Container from 'components/layout/NotificationV1/NotificationV1Container'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import VenueProvidersManagerContainer from '../../VenueProvidersManagerContainer'

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
          <VenueProvidersManagerContainer {...props} />
          <NotificationV1Container />
          <ReactTooltip html />
        </MemoryRouter>
      </Provider>
    )
  })
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
    }

    props = {
      venue,
    }

    pcapi.loadVenueProviders.mockResolvedValue([])

    provider = { id: 'providerId', name: 'Allociné' }
    pcapi.loadProviders.mockResolvedValue([provider])
    createdVenueProvider = {
      id: 'venueProviderId',
      provider,
      providerId: provider.id,
      venueId: props.venue.id,
      venueIdAtOfferProvider: props.venue.siret,
    }
    pcapi.createVenueProvider.mockResolvedValue(createdVenueProvider)

    await renderVenueProvidersManager(props)
  })

  afterEach(() => {
    pcapi.loadVenueProviders.mockReset()
    pcapi.loadProviders.mockReset()
    pcapi.createVenueProvider.mockReset()
  })

  const renderAllocineProviderForm = async () => {
    const importOffersButton = screen.getByText('Importer des offres')
    fireEvent.click(importOffersButton)
    const providersSelect = screen.getByRole('combobox')
    fireEvent.change(providersSelect, { target: { value: provider.id } })
  }

  it('should display the price field with minimum value set to 0', async () => {
    // when
    await renderAllocineProviderForm()

    // then
    const priceField = screen.getByLabelText('Prix de vente/place', { exact: false })
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

  it('should display the isDuo checkbox checked by default', async () => {
    // when
    await renderAllocineProviderForm()

    // then
    const isDuoCheckbox = screen.getByLabelText(`Accepter les réservations DUO`)
    expect(isDuoCheckbox).toBeInTheDocument()
    expect(isDuoCheckbox).toBeChecked()
  })

  it('should display an import button disabled by default', async () => {
    // when
    await renderAllocineProviderForm()

    // then
    const offerImportButton = screen.getByRole('button', { name: 'Importer les offres' })
    expect(offerImportButton).toBeInTheDocument()
    expect(offerImportButton).toHaveAttribute('type', 'submit')
    expect(offerImportButton).toBeDisabled()
  })

  it('should be able to submit when price field is filled', async () => {
    // given
    await renderAllocineProviderForm()
    const offerImportButton = screen.getByRole('button', { name: 'Importer les offres' })
    const priceField = screen.getByLabelText('Prix de vente/place', { exact: false })
    const quantityField = screen.getByLabelText('Nombre de places/séance')
    const isDuoCheckbox = screen.getByLabelText(`Accepter les réservations DUO`)

    // when
    fireEvent.change(priceField, { target: { value: 10 } })
    fireEvent.change(quantityField, { target: { value: 5 } })
    fireEvent.click(isDuoCheckbox)
    fireEvent.click(offerImportButton)

    // then
    expect(pcapi.createVenueProvider).toHaveBeenCalledWith({
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
    const offerImportButton = screen.getByRole('button', { name: 'Importer les offres' })
    const priceField = screen.getByLabelText('Prix de vente/place', { exact: false })

    // when
    fireEvent.change(priceField, { target: { value: 0 } })
    fireEvent.click(offerImportButton)

    // then
    expect(pcapi.createVenueProvider).toHaveBeenCalledWith({
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
    const offerImportButton = screen.getByRole('button', { name: 'Importer les offres' })
    const priceField = screen.getByLabelText('Prix de vente/place', { exact: false })

    // when
    fireEvent.change(priceField, { target: { value: 0.42 } })
    fireEvent.click(offerImportButton)

    // then
    expect(pcapi.createVenueProvider).toHaveBeenCalledWith({
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
    const offerImportButton = screen.getByRole('button', { name: 'Importer les offres' })
    const quantityField = screen.getByLabelText('Nombre de places/séance')

    // when
    fireEvent.change(quantityField, { target: { value: 10 } })
    fireEvent.click(offerImportButton)

    // then
    expect(pcapi.createVenueProvider).toHaveBeenCalledTimes(0)
  })

  it('should display a notification and unselect provider if there is something wrong with the server', async () => {
    // given
    const apiError = {
      errors: { global: ['Le prix ne peut pas être négatif'] },
      status: 400,
    }
    pcapi.createVenueProvider.mockRejectedValue(apiError)
    await renderAllocineProviderForm()
    const offerImportButton = screen.getByRole('button', { name: 'Importer les offres' })
    const priceField = screen.getByLabelText('Prix de vente/place', { exact: false })

    // when
    fireEvent.change(priceField, { target: { value: -10 } })
    await fireEvent.click(offerImportButton)

    // then
    const errorNotification = await screen.findByText(apiError.errors.global[0])
    expect(errorNotification).toBeInTheDocument()
  })
})
