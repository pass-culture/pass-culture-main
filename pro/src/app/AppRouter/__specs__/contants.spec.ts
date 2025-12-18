import { RouteId } from '../constants'
import { findRouteById } from '../findRouteById'

describe('RouteId', () => {
  it.each(
    Object.values(RouteId)
  )('Route with ID %s should exist', (routeId) => {
    expect(() => findRouteById(routeId)).not.toThrow()
  })
})
