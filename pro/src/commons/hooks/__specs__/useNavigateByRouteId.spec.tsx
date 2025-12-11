import { renderHook } from '@testing-library/react'

import { RouteId } from '@/app/AppRouter/constants'

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

    expect(navigateMock).toHaveBeenCalledTimes(1)
  })

  it('should call assertOrFrontendError when the route ID does not exist', async () => {
    const { MemoryRouter } = await import('react-router')

    vi.spyOn(console, 'error').mockImplementation(() => {})

    const { result } = renderHook(() => useNavigateByRouteId(), {
      wrapper: ({ children }) => <MemoryRouter>{children}</MemoryRouter>,
    })
    const call = () => result.current('invalid-route-id' as RouteId)

    expect(call).toThrow('route is undefined (routeId=invalid-route-id).')

    expect(navigateMock).not.toHaveBeenCalled()
  })
})
