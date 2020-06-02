const _extendRoutesWithExact = routes =>
  routes.map(route => {
    const exact = route && route.exact === undefined ? true : route.exact
    const sensitive = route && route.sensitive === undefined ? true : route.sensitive
    const extend = { exact, sensitive }
    return { ...route, ...extend }
  })

export const getBrowserRoutes = routes => _extendRoutesWithExact(routes)
