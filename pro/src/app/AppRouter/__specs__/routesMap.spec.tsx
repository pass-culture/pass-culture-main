import { screen, waitFor } from '@testing-library/react'
import { useLocation } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NavigateToNewPasswordReset } from '../routesMap'

const CurrentPath = () => {
  const { pathname } = useLocation()

  return <span data-testid="current-path">{pathname}</span>
}

describe('NavigateToNewPasswordReset', () => {
  it('should redirect to the password reset page with the token from query params', async () => {
    renderWithProviders(null, {
      initialRouterEntries: ['/mot-de-passe-perdu?token=token-123'],
      routes: [
        {
          element: <NavigateToNewPasswordReset to="/demande-mot-de-passe" />,
          path: '/mot-de-passe-perdu',
        },
        {
          element: <CurrentPath />,
          path: '/demande-mot-de-passe/:token',
        },
      ],
    })

    await waitFor(() => {
      expect(screen.getByTestId('current-path')).toHaveTextContent(
        '/demande-mot-de-passe/token-123'
      )
    })
  })

  it('should support location object destinations', async () => {
    renderWithProviders(null, {
      initialRouterEntries: ['/mot-de-passe-perdu?token=token-456'],
      routes: [
        {
          element: (
            <NavigateToNewPasswordReset
              to={{ pathname: '/demande-mot-de-passe' }}
            />
          ),
          path: '/mot-de-passe-perdu',
        },
        {
          element: <CurrentPath />,
          path: '/demande-mot-de-passe/:token',
        },
      ],
    })

    await waitFor(() => {
      expect(screen.getByTestId('current-path')).toHaveTextContent(
        '/demande-mot-de-passe/token-456'
      )
    })
  })
})
