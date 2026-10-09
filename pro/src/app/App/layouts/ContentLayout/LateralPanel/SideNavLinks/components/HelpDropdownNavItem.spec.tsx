import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { HelpDropdownNavItem } from './HelpDropdownNavItem'

const mockLogEvent = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: mockLogEvent }),
}))

const HELP_ITEMS = [
  {
    name: 'Nouvelle fenêtre Consulter le centre d’aide',
    event: 'hasClickedConsultHelp',
  },
  {
    name: 'Nouvelle fenêtre Contacter nos équipes',
    event: 'hasClickedContactOurTeams',
  },
  {
    name: 'Nouvelle fenêtre Découvrir les nouveautés',
    event: 'hasClickedNewEvolutions',
  },
  {
    name: 'Nouvelle fenêtre Bonnes pratiques et études',
    event: 'hasClickedBestPracticesAndStudies',
  },
] as const

describe('<HelpDropdownNavItem />', () => {
  beforeEach(() => {
    mockLogEvent.mockClear()
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <HelpDropdownNavItem isMobileScreen={false} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it.each(HELP_ITEMS)(
    'should log $event when clicking "$name"',
    async ({ name, event }) => {
      renderWithProviders(<HelpDropdownNavItem isMobileScreen={false} />)

      const user = userEvent.setup()

      await user.click(screen.getByRole('button', { name: 'Centre d’aide' }))
      await user.click(screen.getByRole('menuitem', { name }))

      expect(mockLogEvent).toHaveBeenCalledExactlyOnceWith(event)
    }
  )
})
