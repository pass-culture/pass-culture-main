import routes from '../../../router/routes'

export const getMenuItemsFromRoutes = routes =>
  routes.reduce((accumulator, currentRoute) => {
    if (currentRoute.icon) {
      const extended = {}
      if (currentRoute.path) {
        extended.path = currentRoute.path
          .split('/')
          .slice(0, 2)
          .join('/')
      }
      accumulator.push({ ...currentRoute, ...extended })
    }

    return accumulator
  }, [])

const getMenuItems = getMenuItemsFromRoutes(routes)

export default getMenuItems
