export const getReactRoutes = items =>
  items
    // si un element a une propriete href
    // alors ce n'est pas une route react
    .map(obj => {
      if (!obj || obj.href) return null
      const exact = obj && obj.exact === undefined ? true : obj.exact
      const extend = { exact }
      return { ...obj, ...extend }
    })

export const getMainMenuItems = items =>
  items
    // si un element n'a pas de propriete `icon`
    // alors il ne sera pas affiche dans le menu principal
    .filter(obj => obj && obj.icon)
    .map(obj => {
      if (!obj.path) return obj
      const splitted = obj.path.split('/')
      if (splitted.length <= 1) return obj
      const path = `/${splitted[1]}`
      return Object.assign({}, obj, { path })
    })
