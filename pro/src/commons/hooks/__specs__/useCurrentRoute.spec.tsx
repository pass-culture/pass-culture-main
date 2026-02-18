import { screen } from '@testing-library/react'
import type { RouteObject } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { useCurrentRoute } from '../useCurrentRoute'

const CurrentRouteDisplay = () => {
  const currentRoute = useCurrentRoute()

  return (
    <div>
      <span data-testid="pathname">{currentRoute.pathname}</span>
      <span data-testid="title">{currentRoute.handle?.title ?? ''}</span>
    </div>
  )
}

const renderWithRoute = (routes: RouteObject[], initialPath: string) => {
  renderWithProviders(null, {
    routes,
    initialRouterEntries: [initialPath],
  })
}

describe('useCurrentRoute', () => {
  it('should return the deepest matched route', () => {
    renderWithRoute(
      [
        {
          path: '/',
          children: [
            {
              path: 'child',
              handle: { title: 'Child Page' },
              element: <CurrentRouteDisplay />,
            },
          ],
        },
      ],
      '/child'
    )

    expect(screen.getByTestId('pathname')).toHaveTextContent('/child')
    expect(screen.getByTestId('title')).toHaveTextContent('Child Page')
  })

  it('should return the matched route with its handle metadata', () => {
    renderWithRoute(
      [
        {
          path: '/accueil',
          handle: { title: 'Espace acteurs culturels' },
          element: <CurrentRouteDisplay />,
        },
      ],
      '/accueil'
    )

    expect(screen.getByTestId('pathname')).toHaveTextContent('/accueil')
    expect(screen.getByTestId('title')).toHaveTextContent(
      'Espace acteurs culturels'
    )
  })

  it('should return empty handle title when route has no handle', () => {
    renderWithRoute(
      [
        {
          path: '/no-handle',
          element: <CurrentRouteDisplay />,
        },
      ],
      '/no-handle'
    )

    expect(screen.getByTestId('pathname')).toHaveTextContent('/no-handle')
    expect(screen.getByTestId('title')).toHaveTextContent('')
  })
})
