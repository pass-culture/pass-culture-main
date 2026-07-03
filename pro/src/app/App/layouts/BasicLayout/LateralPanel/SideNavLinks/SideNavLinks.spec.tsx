import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as reactRouterModule from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { makeUseLocationReturn } from '@/commons/utils/tests/mocks/react-router'

import { type NavItem, SideNavLinks } from './SideNavLinks'

vi.mock('@/commons/hooks/useMediaQuery', async (importOriginal) => ({
  ...((await importOriginal()) as any),
  useMediaQuery: vi.fn(),
}))

vi.mock('./components/SideNavLink', () => ({
  RenderNavItem: ({ item, isOpen, onToggleButtonClick }: any) => (
    <li data-testid="render-nav-item">
      <span>{item.title}</span>
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
  const useLocationMock = vi.fn()

  beforeEach(() => {
    vi.spyOn(reactRouterModule, 'useLocation').mockImplementation(
      useLocationMock
    )
  })

  it('renders main nav items and footer items', () => {
    render(<SideNavLinks navItems={navItems} />)

    const mainItems = screen.getAllByTestId('render-nav-item')

    expect(mainItems).toHaveLength(2)
    expect(screen.getByText('Main 1')).toBeInTheDocument()
    expect(screen.getByText('Main 2')).toBeInTheDocument()
    expect(screen.getByTestId('user-review-mock')).toBeInTheDocument()
    expect(screen.getByTestId('help-dropdown')).toBeInTheDocument()
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
    sessionStorage.clear()

    render(<SideNavLinks navItems={navItems} />)

    const toggleBtn1 = screen.getByTestId('toggle-1')
    const toggleBtn2 = screen.getByTestId('toggle-2')

    // Aucune section n'est ouverte par défaut
    expect(toggleBtn1).toHaveTextContent('CLOSED')
    expect(toggleBtn2).toHaveTextContent('CLOSED')

    // Ouvrir la section 1
    await user.click(toggleBtn1)
    expect(toggleBtn1).toHaveTextContent('OPEN')
    expect(toggleBtn2).toHaveTextContent('CLOSED')

    // Ouvrir la section 2 ferme la section 1
    await user.click(toggleBtn2)
    expect(toggleBtn2).toHaveTextContent('OPEN')
    expect(toggleBtn1).toHaveTextContent('CLOSED')

    // Cliquer à nouveau sur la section 2 la ferme
    await user.click(toggleBtn2)
    expect(toggleBtn2).toHaveTextContent('CLOSED')
  })

  it('should open the section matching the current route (individual)', () => {
    useLocationMock.mockReturnValue(
      makeUseLocationReturn({
        pathname: '/offres',
      })
    )

    const navItems: NavItem[] = [
      {
        key: 'individual',
        group: 'main',
        type: 'section',
        title: 'Section individuel',
        children: [
          {
            key: 'offers',
            type: 'link',
            group: 'main',
            title: 'Offres',
            to: '/offres',
            end: true,
          },
        ],
      },
      {
        key: 'collective',
        group: 'main',
        type: 'section',
        title: 'Section collective',
        children: [
          {
            key: 'showcase_offers',
            type: 'link',
            group: 'main',
            title: 'Offres vitrines',
            to: '/offres/vitrines',
          },
        ],
      },
    ]
    render(<SideNavLinks navItems={navItems} />)

    expect(screen.getByText('Section individuel')).toBeInTheDocument()
    expect(screen.getByText('Section collective')).toBeInTheDocument()

    const toggleBtnIndividual = screen.getByTestId('toggle-individual')
    const toggleBtnCollective = screen.getByTestId('toggle-collective')

    expect(toggleBtnIndividual).toHaveTextContent('OPEN') // Mocked route is /offres
    expect(toggleBtnCollective).toHaveTextContent('CLOSED')
  })

  it('should open the section matching the current route (collective)', () => {
    useLocationMock.mockReturnValue(
      makeUseLocationReturn({
        pathname: '/offres/vitrines',
      })
    )

    const navItems: NavItem[] = [
      {
        key: 'individual',
        group: 'main',
        type: 'section',
        title: 'Section individuel',
        children: [
          {
            key: 'offers',
            type: 'link',
            group: 'main',
            title: 'Offres',
            to: '/offres',
            end: true,
          },
        ],
      },
      {
        key: 'collective',
        group: 'main',
        type: 'section',
        title: 'Section collective',
        children: [
          {
            key: 'showcase_offers',
            type: 'link',
            group: 'main',
            title: 'Offres vitrines',
            to: '/offres/vitrines',
          },
        ],
      },
    ]
    render(<SideNavLinks navItems={navItems} />)

    expect(screen.getByText('Section individuel')).toBeInTheDocument()
    expect(screen.getByText('Section collective')).toBeInTheDocument()

    const toggleBtnIndividual = screen.getByTestId('toggle-individual')
    const toggleBtnCollective = screen.getByTestId('toggle-collective')

    expect(toggleBtnIndividual).toHaveTextContent('CLOSED')
    expect(toggleBtnCollective).toHaveTextContent('OPEN') // Mocked route is /offres/vitrines
  })
})
