import { screen, waitFor } from '@testing-library/react'
import { useLocation } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { redirectedRoutes } from '../redirectedRoutes'

vi.mock('@/commons/auth/withUserPermissions', () => ({
  withUserPermissions: () => () => null,
}))

const RouteTester = () => {
  const location = useLocation()

  return (
    <div data-testid="route-location">
      {location.pathname}
      {location.search}
      {location.hash}
    </div>
  )
}

describe('redirectedRoutes', () => {
  it('redirects legacy reimbursements URLs and replaces the history entry', async () => {
    const previousUrl = '/administration/gestion-financiere/__previous__'
    const legacyUrl = '/administration/remboursements?periode=2025#details'

    const { router } = renderWithProviders(
      <></>,
      {
        routes: [
          ...redirectedRoutes,
          {
            path: '/administration/gestion-financiere/*',
            element: <RouteTester />,
          },
        ],
        initialRouterEntries: [previousUrl, legacyUrl],
      },
      legacyUrl
    )

    expect(screen.getByTestId('route-location')).toHaveTextContent(
      '/administration/gestion-financiere/?periode=2025#details'
    )

    await waitFor(() => {
      router.navigate(-1)
    })

    expect(screen.getByTestId('route-location')).toHaveTextContent(previousUrl)
  })
})
