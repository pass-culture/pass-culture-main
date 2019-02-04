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

export const addMenuViewToRoutesWithPath = routes =>
  routes.map(route => {
    const clone = { ...route }
    if (clone.path) {
      clone.path = `${clone.path}/:menu(menu)?`
    }
    return clone
  })

export const getReactRoutes = routes =>
  filterRoutes(addMenuViewToRoutesWithPath(routes))

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
