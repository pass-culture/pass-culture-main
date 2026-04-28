import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { vi } from 'vitest'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Header } from './Header'

describe('Header', () => {
  it('should show "Espace administration" button when isAdminArea is false', () => {
    renderWithProviders(<Header />)
    expect(
      screen.getByRole('link', { name: 'Espace administration' })
    ).toHaveAttribute('href', '/administration/remboursements')
  })

  it('should show "Revenir à l’Espace Partenaire" button when isAdminArea is true', () => {
    renderWithProviders(<Header isAdminArea />)
    expect(
      screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
    ).toHaveAttribute('href', '/accueil')
  })

  it('should hide "Espace administration" button when hideAdminButton is true', () => {
    renderWithProviders(<Header hideAdminButton />)

    expect(
      screen.queryByRole('link', { name: 'Espace administration' })
    ).toBeFalsy()
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
      renderWithProviders(<Header />)
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
      renderWithProviders(<Header isAdminArea />)
      await user.click(
        screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
      )
      expect(mockLogEvent).not.toHaveBeenCalled()
    })
  })
})
