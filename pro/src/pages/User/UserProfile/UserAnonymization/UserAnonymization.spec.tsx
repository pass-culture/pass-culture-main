import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe } from 'vitest'

import { api } from '@/apiClient/api'
import * as logoutModule from '@/commons/store/user/dispatchers/logout'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { useUserAnonymizationEligibility } from './hooks/useUserAnonymizationEligibility'
import { UserAnonymization } from './UserAnonymization'

vi.mock('./hooks/useUserAnonymizationEligibility', () => ({
  useUserAnonymizationEligibility: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    getProAnonymizationEligibility: vi.fn(),
    anonymize: vi.fn(),
  },
}))

const snackBarError = vi.fn()
const snackBarSuccess = vi.fn()

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => ({
    success: snackBarSuccess,
    error: snackBarError,
  }),
}))

const renderUserAnonymization = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<UserAnonymization />, {
    user: sharedCurrentUserFactory({ email: 'user@example.com' }),
    ...options,
  })
}

describe('UserAnonymization', () => {
  const useUserAnonymizationEligibilityMock = vi.mocked(
    useUserAnonymizationEligibility
  )
  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(api.anonymize).mockResolvedValue()
    useUserAnonymizationEligibilityMock.mockReturnValue({
      isLoading: false,
      isEligible: true,
      isSoleUserWithOngoingActivities: false,
    })
  })

  describe('feature flag handling', () => {
    it('should display the anonymization button when feature flag is enabled', () => {
      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      expect(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      ).toBeInTheDocument()
    })

    it('should not display the anonymization button when feature flag is disabled', () => {
      renderUserAnonymization({
        features: [],
      })

      expect(
        screen.queryByRole('button', { name: 'Supprimer mon compte' })
      ).toBeFalsy()
    })
  })

  describe('dialog loading state', () => {
    it('should not display anonymization button while loading eligibility', () => {
      useUserAnonymizationEligibilityMock.mockReturnValue({
        isLoading: true,
        isEligible: false,
        isSoleUserWithOngoingActivities: undefined,
      })

      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      expect(
        screen.queryByRole('button', { name: 'Supprimer mon compte' })
      ).toBeFalsy()
    })
  })

  describe('eligibility scenarios', () => {
    it('should display the anonymization form when user is eligible', async () => {
      useUserAnonymizationEligibilityMock.mockReturnValue({
        isLoading: false,
        isEligible: true,
        isSoleUserWithOngoingActivities: false,
      })

      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      expect(
        screen.getByRole('heading', {
          name: 'Vous êtes sur le point de supprimer votre compte',
        })
      ).toBeInTheDocument()
      expect(
        screen.getByLabelText(/Confirmer votre adresse email/)
      ).toBeInTheDocument()
    })

    it('should display uneligibility message for user without ongoing activities', async () => {
      useUserAnonymizationEligibilityMock.mockReturnValue({
        isLoading: false,
        isEligible: false,
        isSoleUserWithOngoingActivities: false,
      })

      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      expect(
        screen.getByRole('heading', {
          name: 'La suppression de compte n’est pas possible en l’état',
        })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: /Lire la charte des données personnelles/,
        })
      ).toBeInTheDocument()
    })

    it('should display uneligibility message for user with ongoing activities', async () => {
      useUserAnonymizationEligibilityMock.mockReturnValue({
        isLoading: false,
        isEligible: false,
        isSoleUserWithOngoingActivities: true,
      })

      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      expect(
        screen.getByRole('heading', {
          name: 'La suppression de compte n’est pas possible en l’état',
        })
      ).toBeInTheDocument()
      expect(
        screen.getByText(/Des offres ou réservations sont toujours en cours/)
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: /Lire la charte des données personnelles/,
        })
      ).toBeInTheDocument()
    })
  })

  describe('anonymization form', () => {
    it('should call anonymize and dispatch logout when form is submitted', async () => {
      vi.mocked(api.anonymize).mockResolvedValueOnce()
      const logoutSpy = vi.spyOn(logoutModule, 'logout').mockReturnValue({
        type: 'user/logout/pending',
        payload: undefined,
      } as any)

      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      const emailInput = screen.getByLabelText(/Confirmer votre adresse email/)
      await userEvent.type(emailInput, 'user@example.com')

      const submitButton = screen.getByRole('button', {
        name: 'Supprimer mon compte',
      })

      await userEvent.click(submitButton!)

      await waitFor(() => {
        expect(api.anonymize).toHaveBeenCalledOnce()
        expect(logoutSpy).toHaveBeenCalledOnce()
      })
    })

    it('should display an error notification when anonymization fails', async () => {
      vi.mocked(api.anonymize).mockRejectedValueOnce(
        new Error('Anonymization failed')
      )

      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      const emailInput = screen.getByLabelText(/Confirmer votre adresse email/)
      await userEvent.type(emailInput, 'user@example.com')

      const submitButton = screen.getByRole('button', {
        name: 'Supprimer mon compte',
      })

      await userEvent.click(submitButton!)

      await waitFor(() => {
        expect(snackBarError).toHaveBeenCalledWith(
          'Une erreur est survenue. Merci de réessayer plus tard.'
        )
      })
    })
  })

  describe('anonymization form validation', () => {
    it('should display error when email is empty', async () => {
      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      const emailInput = screen.getByLabelText(/Confirmer votre adresse email/)
      await userEvent.click(emailInput)
      await userEvent.tab()

      await waitFor(() => {
        expect(
          screen.getByText(
            'Veuillez renseigner votre email pour confirmer la suppression du compte'
          )
        ).toBeInTheDocument()
      })
    })

    it('should display error when email format is invalid', async () => {
      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      const emailInput = screen.getByLabelText(/Confirmer votre adresse email/)
      await userEvent.type(emailInput, 'invalid-email')
      await userEvent.tab()

      await waitFor(() => {
        expect(
          screen.getByText(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          )
        ).toBeInTheDocument()
      })
    })

    it('should display error when email does not match user email', async () => {
      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      const emailInput = screen.getByLabelText(/Confirmer votre adresse email/)
      await userEvent.type(emailInput, 'different@example.com')
      await userEvent.tab()

      await waitFor(() => {
        expect(
          screen.getByText(
            "L'adresse email ne correspond pas à celle de votre compte"
          )
        ).toBeInTheDocument()
      })
    })

    it('should prevent form submission', async () => {
      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      const emailInput = screen.getByLabelText(/Confirmer votre adresse email/)
      await userEvent.type(emailInput, 'invalid-email')

      const submitButton = screen.getByRole('button', {
        name: 'Supprimer mon compte',
      })
      await userEvent.click(submitButton!)

      await waitFor(() => {
        expect(api.anonymize).toHaveBeenCalledTimes(0)
      })
    })
  })
})
