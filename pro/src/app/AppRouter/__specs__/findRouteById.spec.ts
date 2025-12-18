import { FrontendError } from '@/commons/errors/FrontendError'

import { RouteId } from '../constants'
import { findRouteById } from '../findRouteById'

describe('findRouteById', () => {
  it('should return a route', () => {
    expect(findRouteById(RouteId.Hub)).toMatchObject({
      id: RouteId.Hub,
      path: '/hub',
      title: expect.any(String),
    })
  })

  it('should throw an error for a non-existent route ID', () => {
    vi.spyOn(console, 'error').mockImplementationOnce(vi.fn())

    const call = () => findRouteById('non-existent-route-id' as RouteId)

    expect(call).toThrow(FrontendError)
  })
})
