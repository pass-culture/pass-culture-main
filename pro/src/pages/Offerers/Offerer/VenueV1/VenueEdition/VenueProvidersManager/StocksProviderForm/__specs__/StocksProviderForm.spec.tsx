import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import StocksProviderForm, {
  StocksProviderFormProps,
} from '../StocksProviderForm'

const mockLogEvent = jest.fn()

const renderStocksProviderForm = (props: StocksProviderFormProps) => {
  renderWithProviders(<StocksProviderForm {...props} />)
}

describe('StocksProviderForm', () => {
  let props: StocksProviderFormProps
  const providerId = 66
  const venueId = 1
  const offererId = 3

  beforeEach(() => {
    props = {
      offererId: offererId,
      providerId: providerId,
      saveVenueProvider: jest.fn(),
      siret: '12345678901234',
      venueId: venueId,
      hasOffererProvider: true,
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
  })

  it('should display an import button', async () => {
    renderStocksProviderForm(props)

    expect(
      screen.queryByRole('button', { name: 'Importer les offres' })
    ).toBeInTheDocument()
  })

  describe('on form submit', () => {
    it('should display the spinner while waiting for server response', async () => {
      renderStocksProviderForm(props)
      const submitButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      await userEvent.click(submitButton)

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
      expect(props.saveVenueProvider).toHaveBeenCalledWith({
        providerId: providerId,
        venueId: venueId,
        venueIdAtOfferProvider: '12345678901234',
      })
    })

    it('should track on import', async () => {
      renderStocksProviderForm(props)

      const submitButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      await userEvent.click(submitButton)

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        SynchronizationEvents.CLICKED_IMPORT,
        {
          offererId: offererId,
          venueId: venueId,
          providerId: providerId,
        }
      )

      const confirmImportButton = screen.getByRole('button', {
        name: 'Continuer',
      })
      await userEvent.click(confirmImportButton)

      expect(mockLogEvent).toHaveBeenCalledTimes(2)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        2,
        SynchronizationEvents.CLICKED_VALIDATE_IMPORT,
        {
          offererId: offererId,
          venueId: venueId,
          providerId: providerId,
        }
      )
    })
  })
})
