import { screen, waitFor } from '@testing-library/dom'
import { Outlet, useLocation } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { reimbursementsRouteGroup } from './reimbursementsRouteGroup'

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
describe('reimbursementsRouteGroup', () => {
  it('redirects legacy reimbursements URLs and replaces the history entry', async () => {
    const previousUrl =
      '/administration/gestion-financiere/informations-bancaires'
    const indexUrl = '/administration/gestion-financiere?periode=2025'

    const { router } = renderWithProviders(
      <></>,
      {
        routes: [
          {
            path: '/administration/gestion-financiere',
            element: <Outlet />,
            children: reimbursementsRouteGroup.map((route) =>
              'path' in route
                ? {
                    ...route,
                    lazy: async () => ({ Component: RouteTester }),
                  }
                : route
            ),
          },
        ],
        initialRouterEntries: [previousUrl, indexUrl],
      },
      indexUrl
    )

    await waitFor(() => {
      expect(screen.getByTestId('route-location')).toHaveTextContent(
        '/administration/gestion-financiere/justificatifs?periode=2025'
      )
    })

    await waitFor(() => {
      router.navigate(-1)
    })

    expect(screen.getByTestId('route-location')).toHaveTextContent(previousUrl)
  })
})
