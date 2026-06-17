import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import { ApiError } from '@/apiClient/compat'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { ComplementaryInfosDrawer } from './ComplementaryInfosDrawer'

vi.mock('@/apiClient/api', () => ({
  api: { editVenue: vi.fn() },
}))

vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({ syncVenueWithData: vi.fn() }),
}))

vi.mock(
  '@/pages/VenueEdition/components/AccessibilityForm/AccessibilityForm',
  () => ({
    AccessibilityForm: () => <div data-testid="accessibility-form" />,
  })
)

vi.mock('@/components/OpeningHours/OpeningHours', () => ({
  OpeningHours: () => <div data-testid="opening-hours" />,
}))

const mockLogEvent = vi.fn()

const defaultProps = {
  hasAddressChanged: false,
  open: true,
  onOpenChange: vi.fn(),
}

const renderDialog = (props: Partial<typeof defaultProps> = {}) => {
  renderWithProviders(
    <>
      <ComplementaryInfosDrawer {...defaultProps} {...props} />
      <SnackBarContainer />
    </>,
    {
      storeOverrides: {
        user: {
          selectedPartnerVenue: defaultGetVenue,
        },
      },
    }
  )
}

describe('ComplementaryInfosDrawer', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.mocked(api.editVenue).mockResolvedValue(defaultGetVenue)
  })

  describe('address changed banner', () => {
    it('should show the banner when hasAddressChanged is true', () => {
      renderDialog({ hasAddressChanged: true })

      expect(
        screen.getByText('Vos offres existantes ne sont pas mises à jour')
      ).toBeInTheDocument()
    })

    it('should not show the banner when hasAddressChanged is false', () => {
      renderDialog({ hasAddressChanged: false })

      expect(
        screen.queryByText('Vos offres existantes ne sont pas mises à jour')
      ).not.toBeInTheDocument()
    })
  })

  describe('closing the dialog', () => {
    it('should call onOpenChange(false) when clicking Annuler', async () => {
      const onOpenChange = vi.fn()
      renderDialog({ onOpenChange })

      await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

      expect(onOpenChange).toHaveBeenCalledWith(false)
    })

    it('should call onOpenChange when clicking the close button (X)', async () => {
      const onOpenChange = vi.fn()
      renderDialog({ onOpenChange })

      const closeButton = screen.getByRole('button', { name: /fermer|close/i })
      await userEvent.click(closeButton)

      expect(onOpenChange).toHaveBeenCalledWith(false)
    })
  })

  describe('form submission', () => {
    it('should call editVenue on submit', async () => {
      renderDialog()

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer les informations' })
      )

      await waitFor(() => {
        expect(api.editVenue).toHaveBeenCalledWith({
          path: { venue_id: defaultGetVenue.id },
          body: expect.anything(),
        })
      })
    })

    it('should log a save event with saved: true on success', async () => {
      renderDialog()

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer les informations' })
      )

      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
          saved: true,
          isEdition: true,
        })
      })
    })

    it('should show success snackbar on successful save', async () => {
      renderDialog()

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer les informations' })
      )

      expect(
        await screen.findByText('Vos modifications ont été sauvegardées')
      ).toBeInTheDocument()
    })

    it('should show generic error snackbar when API returns a global error', async () => {
      vi.mocked(api.editVenue).mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          { status: 500, body: {} } as ApiResult,
          'Server error'
        )
      )

      renderDialog()

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer les informations' })
      )

      expect(
        await screen.findByText(
          'Erreur inconnue lors de la sauvegarde de la structure.'
        )
      ).toBeInTheDocument()
    })

    it('should show field error snackbar when API returns field-level errors', async () => {
      const apiError = new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: { audioDisabilityCompliant: 'Champ invalide' },
        } as unknown as ApiResult,
        'Bad Request'
      )
      vi.mocked(api.editVenue).mockRejectedValue(apiError)

      renderDialog()

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer les informations' })
      )

      expect(
        await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )
      ).toBeInTheDocument()
    })

    it('should log a save event with saved: false on error', async () => {
      vi.mocked(api.editVenue).mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          { status: 500, body: {} } as ApiResult,
          'Server error'
        )
      )

      renderDialog()

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer les informations' })
      )

      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
          saved: false,
          isEdition: true,
        })
      })
    })

    it('should show generic error snackbar for non-API errors', async () => {
      vi.mocked(api.editVenue).mockRejectedValue(new Error('network error'))

      renderDialog()

      await userEvent.click(
        screen.getByRole('button', { name: 'Enregistrer les informations' })
      )

      expect(
        await screen.findByText(
          'Erreur inconnue lors de la sauvegarde de la structure.'
        )
      ).toBeInTheDocument()
    })
  })
})
