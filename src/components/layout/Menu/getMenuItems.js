const getMenuItems = routes =>
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

export default getMenuItems
