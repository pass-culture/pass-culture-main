import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import AllocineProviderForm, {
  AllocineProviderFormProps,
  initialValuesProps,
} from '../AllocineProviderForm'

const mockLogEvent = jest.fn()

const renderAllocineProviderForm = async (props: AllocineProviderFormProps) => {
  renderWithProviders(<AllocineProviderForm {...props} />)
  await waitFor(() => {
    screen.getByText('Prix de vente/place')
  })
}

describe('components | AllocineProviderForm', () => {
  let props: AllocineProviderFormProps
  const venueId = 1
  const providerId = 2
  const provider = { id: providerId, name: 'Allociné', isDuo: true }

  beforeEach(async () => {
    props = {
      venueId: venueId,
      saveVenueProvider: jest.fn(),
      providerId: providerId,
      offererId: 36,
      onCancel: jest.fn(),
      initialValues: { isDuo: true } as initialValuesProps,
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
  })

  it('should display the price field with minimum value set to 0', async () => {
    // when
    await renderAllocineProviderForm(props)

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
    await renderAllocineProviderForm(props)

    // then
    const quantityField = screen.getByLabelText(`Nombre de places/séance`)
    expect(quantityField).toBeInTheDocument()
    expect(quantityField).toHaveAttribute('min', '0')
    expect(quantityField).toHaveAttribute('step', '1')
  })

  describe('import form allocine provider for the first time', () => {
    beforeEach(async () => {
      props.isCreatedEntity = true
    })

    it('should display the isDuo checkbox checked by default', async () => {
      // when
      await renderAllocineProviderForm(props)

      // then
      const isDuoCheckbox = screen.getByLabelText(
        `Accepter les réservations DUO`
      )
      expect(isDuoCheckbox).toBeInTheDocument()
      expect(isDuoCheckbox).toBeChecked()
    })

    it('should display an import button disabled by default', async () => {
      // when
      await renderAllocineProviderForm(props)

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
      await renderAllocineProviderForm(props)

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
      expect(props.saveVenueProvider).toHaveBeenCalledWith({
        price: 10,
        quantity: 5,
        isDuo: false,
        providerId: provider.id,
        venueId: venueId,
      })
    })

    it('should be able to submit when price field is filled to 0', async () => {
      // given
      await renderAllocineProviderForm(props)
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
      expect(props.saveVenueProvider).toHaveBeenCalledWith({
        price: 0,
        quantity: undefined,
        isDuo: true,
        providerId: provider.id,
        venueId: venueId,
      })
    })

    it('should be able to submit when price field is filled with a decimal', async () => {
      // given
      await renderAllocineProviderForm(props)
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
      expect(props.saveVenueProvider).toHaveBeenCalledWith({
        price: 0.42,
        quantity: undefined,
        isDuo: true,
        providerId: provider.id,
        venueId: venueId,
      })
    })

    it('should track on import', async () => {
      // given
      await renderAllocineProviderForm(props)
      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      await userEvent.type(priceField, '10')

      // when
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      await userEvent.click(offerImportButton)

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        SynchronizationEvents.CLICKED_IMPORT,
        {
          offererId: 36,
          venueId: 1,
          providerId: 2,
        }
      )
    })
  })

  describe('edit existing allocine provider', () => {
    beforeEach(() => {
      props.isCreatedEntity = false
      props.initialValues.price = 15
      props.initialValues.quantity = 50
      props.initialValues.isDuo = false
    })

    it('should display modify and cancel button', async () => {
      // when
      await renderAllocineProviderForm(props)

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
      await renderAllocineProviderForm(props)

      const priceField = screen.getByLabelText('Prix de vente/place', {
        exact: false,
      })
      expect(priceField).toHaveValue(15)

      const quantityField = screen.getByLabelText('Nombre de places/séance', {
        exact: false,
      })
      expect(quantityField).toHaveValue(50)

      const isDuoField = screen.getByLabelText(
        'Accepter les réservations DUO',
        { exact: false }
      )
      expect(isDuoField).not.toBeChecked()
    })

    it('should not be able to submit when price field is not filled', async () => {
      // given
      await renderAllocineProviderForm(props)

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
      await renderAllocineProviderForm(props)

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
      await userEvent.type(priceField, '5')
      await userEvent.type(quantityField, '17')

      await userEvent.click(isDuoCheckbox)
      await userEvent.click(saveEditioProvider)

      // then
      expect(props.saveVenueProvider).toHaveBeenCalledWith({
        price: 5,
        quantity: 17,
        isDuo: true,
        providerId: provider.id,
        venueId: 1,
      })
    })
  })
})
