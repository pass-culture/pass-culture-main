const getMenuItems = routes =>
  routes.reduce((accumulator, currentRoute) => {
    if (currentRoute.icon) {
      if (currentRoute.href) {
        accumulator.push(currentRoute)
      } else if (currentRoute.path) {
        const path = currentRoute.path
          .split('/')
          .slice(0, 2)
          .join('/')

        accumulator.push({ ...currentRoute, ...{ path } })
      }
    }

    return accumulator
  }, [])

export default getMenuItems
