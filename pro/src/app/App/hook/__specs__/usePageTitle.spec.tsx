import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import type { RouteObject } from 'react-router'
import { Link, Outlet } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { PageTitleAnnouncer } from '@/components/PageTitleAnnouncer/PageTitleAnnouncer'

import { usePageTitle } from '../usePageTitle'

const PageTitle = (): null => {
  usePageTitle()
  return null
}

const pageTitleRoutes: RouteObject[] = [
  {
    element: (
      <>
        <PageTitle />
        <PageTitleAnnouncer />
        <Outlet />
      </>
    ),
    children: [
      {
        path: '/accueil',
        handle: { title: 'Espace acteurs culturels' },
        element: (
          <>
            <span>Main page</span>
            <Link to="/guichet">Guichet</Link>
          </>
        ),
      },
      {
        path: '/guichet',
        handle: { title: 'Guichet' },
        element: <span>Guichet page</span>,
      },
    ],
  },
]

const renderUsePageTitle = (url = '/accueil') => {
  renderWithProviders(null, {
    routes: pageTitleRoutes,
    initialRouterEntries: [url],
  })
}

describe('usePageTitle', () => {
  it('should set initial page title', () => {
    renderUsePageTitle()
    expect(document.title).toEqual(
      'Espace acteurs culturels - pass Culture Pro'
    )
  })

  it('should update page title when user navigates to another page', async () => {
    renderUsePageTitle()
    await userEvent.click(screen.getByRole('link', { name: 'Guichet' }))
    expect(document.title).toEqual('Guichet - pass Culture Pro')
  })

  it('should update aria pane name announcer region when user navigates to another page', async () => {
    renderUsePageTitle()
    await userEvent.click(screen.getByRole('link', { name: 'Guichet' }))
    const pageTitleAnnouncer = screen.getByTestId('page-title-announcer')
    expect(pageTitleAnnouncer).toHaveTextContent('Guichet')
  })
})
