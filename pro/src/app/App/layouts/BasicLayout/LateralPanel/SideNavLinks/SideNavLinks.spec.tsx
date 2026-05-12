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

vi.mock('./components/UserReviewDialog/UserReviewDialog', () => ({
  UserReviewDialog: ({ dialogTrigger, isAdminSpace }: any) => (
    <div
      data-testid="user-review-mock"
      data-is-admin-space={String(Boolean(isAdminSpace))}
    >
      {dialogTrigger}
    </div>
  ),
}))

vi.mock('./components/HelpDropdownNavItem', () => ({
  HelpDropdownNavItem: ({ isMobileScreen }: { isMobileScreen: boolean }) => (
    <div data-testid="help-dropdown">
      Help - {isMobileScreen ? 'mobile' : 'desktop'}
    </div>
  ),
}))

const navItems: NavItem[] = [
  { key: '1', group: 'main', type: 'section', title: 'Main 1' },
  { key: '2', group: 'main', type: 'section', title: 'Main 2' },
  { key: '3', group: 'footer', type: 'link', title: 'Footer 1' },
]

describe('SideNavLinks', () => {
  it('renders main nav items and footer items', () => {
    render(<SideNavLinks navItems={navItems} />)

    const mainItems = screen.getAllByTestId('render-nav-item')

    expect(mainItems).toHaveLength(2)
    expect(screen.getByText('Main 1')).toBeInTheDocument()
    expect(screen.getByText('Main 2')).toBeInTheDocument()
    expect(screen.getByTestId('user-review-mock')).toBeInTheDocument()
    expect(screen.getByTestId('help-dropdown')).toBeInTheDocument()
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

    render(<SideNavLinks navItems={itemsWithNotification} />)

    expect(screen.getByTestId('nav-item-notification')).toBeInTheDocument()
  })

  it('should forward isAdminSpace=false to UserReviewDialog by default', () => {
    render(<SideNavLinks navItems={navItems} />)

    expect(screen.getByTestId('user-review-mock')).toHaveAttribute(
      'data-is-admin-space',
      'false'
    )
  })

  it('should forward isAdminSpace=true to UserReviewDialog when set', () => {
    render(<SideNavLinks isAdminSpace navItems={navItems} />)

    expect(screen.getByTestId('user-review-mock')).toHaveAttribute(
      'data-is-admin-space',
      'true'
    )
  })

  it('should toggle active section correctly', async () => {
    const user = userEvent.setup()

    // On force explicitement MOBILE (donc état initial = CLOSED)
    vi.mocked(mediaQueryHook.useMediaQuery).mockReturnValue(true)

    render(<SideNavLinks navItems={navItems} />)

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
