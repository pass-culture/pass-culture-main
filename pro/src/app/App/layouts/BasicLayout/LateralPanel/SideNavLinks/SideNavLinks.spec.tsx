import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { type NavItem, SideNavLinks } from './SideNavLinks'

vi.mock('@/commons/hooks/useMediaQuery', async (importOriginal) => ({
  ...(await importOriginal()),
  useMediaQuery: vi.fn(),
}))

vi.mock('./components/SideNavLink', () => ({
  RenderNavItem: ({ item }: { item: NavItem }) => (
    <li data-testid="render-nav-item">{item.title}</li>
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
  { key: '1', group: 'main', type: 'link', title: 'Main 1' },
  { key: '2', group: 'main', type: 'link', title: 'Main 2' },
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

  it('renders footer nav items when switch venue feature is false', () => {
    render(<SideNavLinks navItems={navItems} withSwitchVenueFeature={false} />)

    expect(screen.getByText('Footer 1')).toBeInTheDocument()
    expect(screen.queryByTestId('user-review-dialog')).not.toBeInTheDocument()
    expect(screen.queryByTestId('help-dropdown')).not.toBeInTheDocument()
  })
})
