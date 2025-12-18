import { renderHook } from '@testing-library/react'

import { RouteId } from '@/app/AppRouter/constants'
import { FrontendError } from '@/commons/errors/FrontendError'

import { useNavigateByRouteId } from '../useNavigateByRouteId'

const navigateMock = vi.fn()
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(() => navigateMock),
}))

describe('useNavigateByRouteId()', () => {
  it('should navigate to Homepage route', async () => {
    const { MemoryRouter } = await import('react-router')

    const { result } = renderHook(() => useNavigateByRouteId(), {
      wrapper: ({ children }) => <MemoryRouter>{children}</MemoryRouter>,
    })

    result.current(RouteId.Homepage)

    expect(navigateMock).toHaveBeenCalledExactlyOnceWith('/accueil')
  })

  it('should call log a FrontendError and redirect to error page when the route ID does not exist', async () => {
    const { MemoryRouter } = await import('react-router')

    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {})

    const { result } = renderHook(() => useNavigateByRouteId(), {
      wrapper: ({ children }) => <MemoryRouter>{children}</MemoryRouter>,
    })

    result.current('invalid-route-id' as RouteId)

    expect(consoleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(FrontendError)
    )
    expect(navigateMock).toHaveBeenCalledExactlyOnceWith('/error')
  })
})
