import * as Sentry from '@sentry/react'
import { render, screen, waitFor } from '@testing-library/react'
import * as router from 'react-router-dom'

import { ErrorBoundary } from '../ErrorBoundary'

vi.mock('@sentry/react', () => ({
  captureException: vi.fn(),
}))
vi.mock('react-router-dom', () => ({
  useRouteError: vi.fn(),
}))

const reloadFn = vi.fn()
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: {
    reload: reloadFn,
    href: '',
  },
  writable: true,
})

describe('ErrorBoundary', () => {
  it('should capture exception with Sentry', async () => {
    const error = new Error('Some error')
    vi.spyOn(router, 'useRouteError').mockReturnValue(error)

    render(<ErrorBoundary />)

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
    expect(screen.getByText(/Revenir à l’accueil/)).toBeInTheDocument()
    await waitFor(() => {
      expect(Sentry.captureException).toHaveBeenCalledWith(error)
    })
    expect(reloadFn).not.toHaveBeenCalled()
  })

  it('should reload and not call sentry when the error is a module import error', () => {
    vi.spyOn(router, 'useRouteError').mockReturnValue(
      new Error('dynamically imported module')
    )
    render(<ErrorBoundary />)

    expect(Sentry.captureException).not.toHaveBeenCalled()
    expect(reloadFn).toHaveBeenCalled()
  })

  it('should not show the redirect link when the user is within the adage iframe', () => {
    const error = new Error('Some error')
    vi.spyOn(router, 'useRouteError').mockReturnValue(error)

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        reload: reloadFn,
        href: '/adage-iframe',
      },
      writable: true,
    })

    render(<ErrorBoundary />)

    expect(screen.queryByText(/Revenir à l’accueil/)).not.toBeInTheDocument()
  })
})
