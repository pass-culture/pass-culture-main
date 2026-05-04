import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'

import { HelpDropdownMenu } from './HelpDropdownMenu'

const mockLogEvent = vi.fn()

const renderHelpDropdownMenu = () => {
  renderWithProviders(
    <Dropdown
      title="Centre d'aide"
      trigger={<button type="button">Centre d'aide</button>}
    >
      <HelpDropdownMenu />
    </Dropdown>
  )
}

describe('HelpDropdownMenu', () => {
  describe('trackers', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
    })

    it('should track consult help click', async () => {
      renderHelpDropdownMenu()

      await userEvent.click(
        screen.getByRole('button', { name: "Centre d'aide" })
      )
      await userEvent.click(
        screen.getByRole('menuitem', { name: 'Consulter le centre d’aide' })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_CONSULT_HELP, {
        from: '/',
      })
    })

    it('should track contact our teams click', async () => {
      renderHelpDropdownMenu()

      await userEvent.click(
        screen.getByRole('button', { name: "Centre d'aide" })
      )
      await userEvent.click(
        screen.getByRole('menuitem', { name: 'Contacter nos équipes' })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.CLICKED_CONTACT_OUR_TEAMS,
        {
          from: '/',
        }
      )
    })

    it('should track discover new features click', async () => {
      renderHelpDropdownMenu()

      await userEvent.click(
        screen.getByRole('button', { name: "Centre d'aide" })
      )
      await userEvent.click(
        screen.getByRole('menuitem', { name: 'Découvrir les nouveautés' })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.CLICKED_BEST_PRACTICES_STUDIES,
        {
          from: '/',
        }
      )
    })

    it('should track best practices and studies click', async () => {
      renderHelpDropdownMenu()

      await userEvent.click(
        screen.getByRole('button', { name: "Centre d'aide" })
      )
      await userEvent.click(
        screen.getByRole('menuitem', { name: 'Bonnes pratiques et études' })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_NEW_EVOLUTIONS, {
        from: '/',
      })
    })
  })
})
