import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as logoutModule from '@/commons/store/user/dispatchers/logout'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { UserAnonymization } from './UserAnonymization'

const renderUserAnonymization = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<UserAnonymization />, {
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

vi.mock('@/apiClient/api', () => ({
  api: {
    anonymize: vi.fn(),
  },
}))

const mockNotify = {
  success: vi.fn(),
  error: vi.fn(),
}

vi.mock('@/commons/hooks/useNotification', () => ({
  useNotification: () => mockNotify,
}))

describe('UserAnonymization', () => {
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

  it('should call anonymize and dispatch logout when button is clicked', async () => {
    vi.mocked(api.anonymize).mockResolvedValueOnce()
    const logoutSpy = vi.spyOn(logoutModule, 'logout').mockReturnValue({
      type: 'user/logout/pending',
      payload: undefined,
      // biome-ignore lint/suspicious/noExplicitAny: Mocking complex Redux Thunk return type
    } as any)

    renderUserAnonymization({
      features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
    })

    const button = screen.getByRole('button', { name: 'Supprimer mon compte' })
    await userEvent.click(button)

    expect(api.anonymize).toHaveBeenCalledOnce()
    expect(logoutSpy).toHaveBeenCalledOnce()
  })

  it('should display an error notification when anonymization fails', async () => {
    vi.mocked(api.anonymize).mockRejectedValueOnce(
      new Error('Anonymization failed')
    )
    renderUserAnonymization({
      features: ['WIP_PRO_AUTONOMOUS_ANONYMIZATION'],
    })

    const button = screen.getByRole('button', { name: 'Supprimer mon compte' })
    await userEvent.click(button)

    await waitFor(() => {
      expect(mockNotify.error).toHaveBeenCalledWith(
        'Une erreur est survenue. Merci de réessayer plus tard.'
      )
    })
  })
})
