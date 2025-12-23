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
    user: sharedCurrentUserFactory(),
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
      ).not.toBeInTheDocument()
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
      ).not.toBeInTheDocument()
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
        // biome-ignore lint/suspicious/noExplicitAny: Mocking complex Redux Thunk return type
      } as any)

      renderUserAnonymization({
        features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer mon compte' })
      )

      const emailInput = screen.getByLabelText(/Confirmer votre adresse email/)
      await userEvent.type(emailInput, 'test@example.com')

      const submitButton = screen.getByTestId('user-anonymization-submit')

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
      await userEvent.type(emailInput, 'test@example.com')

      const submitButton = screen.getByTestId('user-anonymization-submit')

      await userEvent.click(submitButton!)

      await waitFor(() => {
        expect(snackBarError).toHaveBeenCalledWith(
          'Une erreur est survenue. Merci de réessayer plus tard.'
        )
      })
    })
  })
})
