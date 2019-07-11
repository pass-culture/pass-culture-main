import { pipe } from '../../utils/functionnals'

const removeHrefRoutes = routes =>
  routes.filter(route => !route.href)

const removeDisabledRoutes = routes =>
  routes.filter(route => !route.disabled)

const extendRoutesWithExact = routes =>
  routes.map(obj => {
    const exact = obj && obj.exact === undefined ? true : obj.exact
    const extend = { exact }
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

const getBrowserRoutes = routes => pipe(
  addMenuViewToRoutesWithPath,
  removeHrefRoutes,
  removeDisabledRoutes,
  extendRoutesWithExact,
)(routes)

export default getBrowserRoutes
