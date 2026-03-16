import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { vi } from 'vitest'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Header } from './Header'

const defaultProps = {
  hasLateralMenu: false,
  lateralPanelOpen: false,
  setLateralPanelOpen: vi.fn(),
  focusCloseButton: vi.fn(),
  disableHomeLink: false,
  isAdminArea: false,
}

describe('Header', () => {
  it('should show "Espace administration" button when FF is enabled and isAdminArea is false', () => {
    renderWithProviders(<Header {...defaultProps} />, {
      features: ['WIP_SWITCH_VENUE'],
    })
    expect(
      screen.getByRole('link', { name: 'Espace administration' })
    ).toHaveAttribute('href', '/remboursements')
  })

  it('should show "Revenir à l’Espace Partenaire" button when FF is enabled and isAdminArea is true', () => {
    renderWithProviders(<Header {...defaultProps} isAdminArea={true} />, {
      features: ['WIP_SWITCH_VENUE'],
    })
    expect(
      screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
    ).toHaveAttribute('href', '/accueil')
  })

  it('should show "Revenir à l’Espace Partenaire" button when FF is enabled and isAdminArea is true', () => {
    renderWithProviders(<Header {...defaultProps} isAdminArea={true} />, {
      features: ['WIP_SWITCH_VENUE'],
    })
    expect(
      screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
    ).toHaveAttribute('href', '/accueil')
  })

  describe('logEvents', () => {
    const mockLogEvent = vi.fn()
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
    })

    it('should track "Espace administration" button click', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Header {...defaultProps} />, {
        features: ['WIP_SWITCH_VENUE'],
      })
      await user.click(
        screen.getByRole('link', { name: 'Espace administration' })
      )
      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.CLICKED_HEADER_ADMIN_BUTTON,
        {
          from: '/',
        }
      )
    })

    it('should NOT track "Revenir à l’Espace Partenaire" button click', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Header {...defaultProps} isAdminArea={true} />, {
        features: ['WIP_SWITCH_VENUE'],
      })
      await user.click(
        screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
      )
      expect(mockLogEvent).not.toHaveBeenCalled()
    })
  })
})
