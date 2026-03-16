import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { vi } from 'vitest'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Header } from './Header'

describe('Header', () => {
  describe('with WIP_SWITCH_VENUE feature flag', () => {
    it('should show "Espace administration" button when isAdminArea is false', () => {
      renderWithProviders(<Header />, {
        features: ['WIP_SWITCH_VENUE'],
      })
      expect(
        screen.getByRole('link', { name: 'Espace administration' })
      ).toHaveAttribute('href', '/remboursements')
    })

    it('should show "Revenir à l’Espace Partenaire" button when isAdminArea is true', () => {
      renderWithProviders(<Header isAdminArea />, {
        features: ['WIP_SWITCH_VENUE'],
      })
      expect(
        screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
      ).toHaveAttribute('href', '/accueil')
    })

    it('should hide "Espace administration" button when hideAdminButton is true', () => {
      renderWithProviders(<Header hideAdminButton />, {
        features: ['WIP_SWITCH_VENUE'],
      })

      expect(
        screen.queryByRole('link', { name: 'Espace administration' })
      ).toBeFalsy()
    })
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
      renderWithProviders(<Header />, {
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
      renderWithProviders(<Header isAdminArea />, {
        features: ['WIP_SWITCH_VENUE'],
      })
      await user.click(
        screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
      )
      expect(mockLogEvent).not.toHaveBeenCalled()
    })
  })
})
