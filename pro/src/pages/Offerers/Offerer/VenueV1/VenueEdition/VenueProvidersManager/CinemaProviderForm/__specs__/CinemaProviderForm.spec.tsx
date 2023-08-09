import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  CinemaProviderForm,
  CinemaProviderFormProps,
} from '../CinemaProviderForm'
import { CinemaProviderFormValues } from '../types'

const mockLogEvent = vi.fn()

const renderCinemaProviderForm = async (props: CinemaProviderFormProps) => {
  renderWithProviders(<CinemaProviderForm {...props} />)

  await waitFor(() => screen.getByText('Accepter les réservations DUO'))
}

describe('CinemaProviderForm', () => {
  let props: CinemaProviderFormProps
  const providerId = 66
  const venueId = 1
  const offererId = 3

  beforeEach(async () => {
    props = {
      saveVenueProvider: vi.fn().mockReturnValue(true),
      providerId: providerId,
      venueId: venueId,
      offererId: offererId,
      isCreatedEntity: true,
      onCancel: vi.fn(),
      initialValues: { isDuo: true } as CinemaProviderFormValues,
    }

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...vi.importActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
  })

  describe('import form cinema provider for the first time', () => {
    it('should display the isDuo checkbox checked by default', async () => {
      await renderCinemaProviderForm(props)

      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )
      expect(isDuoCheckbox).toBeInTheDocument()
      expect(isDuoCheckbox).toBeChecked()
    })

    it('should display import button', async () => {
      await renderCinemaProviderForm(props)

      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      expect(offerImportButton).toBeInTheDocument()
    })

    it('should track on import', async () => {
      await renderCinemaProviderForm(props)
      const offersImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      await userEvent.click(offersImportButton)

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        SynchronizationEvents.CLICKED_IMPORT,
        {
          offererId: offererId,
          venueId: venueId,
          providerId: providerId,
          saved: true,
        }
      )
    })
  })

  describe('edit existing cinema provider', () => {
    beforeEach(() => {
      props.isCreatedEntity = false
      props.initialValues = { isDuo: false, isActive: false }
    })

    it('should display modify and cancel button', async () => {
      await renderCinemaProviderForm(props)

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
      await renderCinemaProviderForm(props)

      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )
      expect(isDuoCheckbox).not.toBeChecked()
    })
  })
})
