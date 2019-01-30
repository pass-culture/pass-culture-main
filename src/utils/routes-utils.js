// NOTE: le filter pour supprimer les éléments `null`
// augmente les tests unitaires de 3s

export const filterRoutes = items =>
  items
    // si un element a une propriete href
    // alors ce n'est pas une route react
    .map(obj => {
      if (!obj || obj.href) return null
      const exact = obj && obj.exact === undefined ? true : obj.exact
      const extend = { exact }
      return { ...obj, ...extend }
    })

export const addMenuRoutes = routes =>
  routes.map(route => {
    if (route.path) {
      route.path = `${route.path}/:menu(menu)?`
    }
    return route
  })

export const getReactRoutes = routes => filterRoutes(addMenuRoutes(routes))

export const getMainMenuItems = items =>
  items
    // si un element n'a pas de propriete `icon`
    // alors il ne sera pas affiche dans le menu principal
    .map(obj => {
      if (!obj.icon || (!obj.path && !obj.href)) return null
      if (!obj.path || obj.href) return obj
      const path = obj.path
        .split('/')
        .slice(0, 2)
        .join('/')
      return Object.assign({}, obj, { path })
    })
