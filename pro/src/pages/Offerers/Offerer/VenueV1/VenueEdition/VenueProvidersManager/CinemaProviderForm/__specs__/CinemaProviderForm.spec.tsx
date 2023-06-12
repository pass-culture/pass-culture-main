import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  CinemaProviderForm,
  ICinemaProviderFormProps,
} from '../CinemaProviderForm'
import { ICinemaProviderFormValues } from '../types'

const mockLogEvent = jest.fn()

const renderCinemaProviderForm = async (props: ICinemaProviderFormProps) => {
  renderWithProviders(<CinemaProviderForm {...props} />)

  await waitFor(() => screen.getByText('Accepter les réservations DUO'))
}

describe('components | CinemaProviderForm', () => {
  let props: ICinemaProviderFormProps

  beforeEach(async () => {
    props = {
      saveVenueProvider: jest.fn(),
      providerId: 66,
      venueId: 1,
      offererId: 3,
      isCreatedEntity: true,
      onCancel: jest.fn(),
      initialValues: { isDuo: true } as ICinemaProviderFormValues,
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
  })

  describe('import form cinema provider for the first time', () => {
    beforeEach(() => {})

    it('should display the isDuo checkbox checked by default', async () => {
      // when
      await renderCinemaProviderForm(props)

      // then
      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )
      expect(isDuoCheckbox).toBeInTheDocument()
      expect(isDuoCheckbox).toBeChecked()
    })

    it('should display import button', async () => {
      // when
      await renderCinemaProviderForm(props)

      // then
      const offerImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })
      expect(offerImportButton).toBeInTheDocument()
      expect(offerImportButton).toHaveAttribute('type', 'submit')
    })

    it('should track on import', async () => {
      // given
      await renderCinemaProviderForm(props)
      const offersImportButton = screen.getByRole('button', {
        name: 'Importer les offres',
      })

      // when
      await userEvent.click(offersImportButton)

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        SynchronizationEvents.CLICKED_IMPORT,
        {
          offererId: 3,
          venueId: 1,
          providerId: 66,
        }
      )
    })
  })

  describe('edit existing cinema provider', () => {
    beforeEach(() => {
      props.isCreatedEntity = false
      props.initialValues.isDuo = false
    })

    it('should display modify and cancel button', async () => {
      // when
      await renderCinemaProviderForm(props)

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
      await renderCinemaProviderForm(props)

      const isDuoCheckbox = screen.getByLabelText(
        'Accepter les réservations DUO'
      )
      expect(isDuoCheckbox).not.toBeChecked()
    })
  })
})
