import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import * as mediaQueryHook from '@/commons/hooks/useMediaQuery'

import { type NavItem, SideNavLinks } from './SideNavLinks'

vi.mock('@/commons/hooks/useMediaQuery', async (importOriginal) => ({
  ...((await importOriginal()) as any),
  useMediaQuery: vi.fn(),
}))

vi.mock('./components/SideNavLink', () => ({
  RenderNavItem: ({ item, isOpen, onToggleButtonClick }: any) => (
    <li data-testid="render-nav-item">
      <span>{item.title}</span>
      {item.showNotification && <span data-testid="nav-item-notification" />}
      <button
        onClick={() => onToggleButtonClick?.(!isOpen)}
        data-testid={`toggle-${item.key}`}
      >
        {isOpen ? 'OPEN' : 'CLOSED'}
      </button>
    </li>
  ),
}))

vi.mock('./components/HelpDropdownNavItem', () => ({
  HelpDropdownNavItem: ({ isMobileScreen }: { isMobileScreen: boolean }) => (
    <li data-testid="help-dropdown">
      Help - {isMobileScreen ? 'mobile' : 'desktop'}
    </li>
  ),
}))

const navItems: NavItem[] = [
  { key: '1', group: 'main', type: 'section', title: 'Main 1' },
  { key: '2', group: 'main', type: 'section', title: 'Main 2' },
  { key: '3', group: 'footer', type: 'link', title: 'Footer 1' },
]

describe('SideNavLinks', () => {
  it('renders main nav items', () => {
    render(<SideNavLinks navItems={navItems} withSwitchVenueFeature={false} />)

    const renderedItems = screen.getAllByTestId('render-nav-item')

    expect(renderedItems).toHaveLength(3)
    expect(screen.getByText('Main 1')).toBeInTheDocument()
    expect(screen.getByText('Main 2')).toBeInTheDocument()
  })

  it('should pass showNotification to nav items', () => {
    const itemsWithNotification: NavItem[] = [
      {
        key: 'with-notif',
        group: 'main',
        type: 'link',
        title: 'With notification',
        showNotification: true,
      },
    ]

    render(
      <SideNavLinks
        navItems={itemsWithNotification}
        withSwitchVenueFeature={false}
      />
    )

    expect(screen.getByTestId('nav-item-notification')).toBeInTheDocument()
  })

  it('renders footer nav items when switch venue feature is false', () => {
    render(<SideNavLinks navItems={navItems} withSwitchVenueFeature={false} />)

    expect(screen.getByText('Footer 1')).toBeInTheDocument()
    expect(screen.queryByTestId('user-review-dialog')).not.toBeInTheDocument()
    expect(screen.queryByTestId('help-dropdown')).not.toBeInTheDocument()
  })

  it('should toggle active section correctly', async () => {
    const user = userEvent.setup()

    // On force explicitement MOBILE (donc état initial = CLOSED)
    vi.mocked(mediaQueryHook.useMediaQuery).mockReturnValue(true)

    render(<SideNavLinks navItems={navItems} withSwitchVenueFeature={false} />)

    const toggleBtn1 = screen.getByTestId('toggle-1')

    // Vérification initiale
    expect(toggleBtn1).toHaveTextContent('CLOSED')

    // Clic
    await user.click(toggleBtn1)

    // Attente du changement
    await waitFor(() => {
      expect(toggleBtn1).toHaveTextContent('OPEN')
    })
  })
})
