import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  StocksProviderForm,
  StocksProviderFormProps,
} from '../StocksProviderForm'

const mockLogEvent = vi.fn()

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
      saveVenueProvider: vi.fn().mockReturnValue(true),
      siret: '12345678901234',
      venueId: venueId,
      hasOffererProvider: true,
    }

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...vi.importActual('app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))
  })

  it('should display an import button', () => {
    renderStocksProviderForm(props)

    expect(
      screen.queryByRole('button', { name: 'Lancer la synchronisation' })
    ).toBeInTheDocument()
  })

  describe('on form submit', () => {
    it('should display the spinner while waiting for server response', async () => {
      renderStocksProviderForm(props)
      const submitButton = screen.getByRole('button', {
        name: 'Lancer la synchronisation',
      })

      await userEvent.click(submitButton)

      expect(
        screen.getByText(
          'Demander la synchronisation par API avec un logiciel tiers ?'
        )
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
        name: 'Lancer la synchronisation',
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
          saved: true,
        }
      )
    })
  })
})
