import { pipe } from '../../utils/functionnals'

const removeHrefRoutes = routes => routes.filter(route => !route.href)

const extendRoutesWithExact = routes =>
  routes.map(obj => {
    const exact = obj && obj.exact === undefined ? true : obj.exact
    const sensitive = obj && obj.sensitive === undefined ? true : obj.sensitive
    const extend = { exact, sensitive }
    return { ...obj, ...extend }
  })

const addMenuViewToRoutesWithPath = routes =>
  routes.map(route => {
    const clone = { ...route }
    if (clone.path) {
      clone.path = `${clone.path}/:menu(menu)?`
    }
    return clone
  })

const getBrowserRoutes = routes =>
  pipe(
    addMenuViewToRoutesWithPath,
    removeHrefRoutes,
    extendRoutesWithExact
  )(routes)

export default getBrowserRoutes
