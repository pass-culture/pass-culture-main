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

describe('ErrorBoundary', () => {
  it('should capture exception with Sentry', async () => {
    const error = new Error('Some error')
    vi.spyOn(router, 'useRouteError').mockReturnValue(error)

    render(<ErrorBoundary />)

    expect(screen.getByText('Page indisponible')).toBeInTheDocument()
    await waitFor(() => {
      expect(Sentry.captureException).toHaveBeenCalledWith(error)
    })
  })

  it('should not call sentry when the error is a module import error', () => {
    vi.spyOn(router, 'useRouteError').mockReturnValue(
      new Error('dynamically imported module')
    )
    render(<ErrorBoundary />)

    expect(Sentry.captureException).not.toHaveBeenCalled()
  })
})
