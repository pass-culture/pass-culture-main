export const redirectLoggedUser = (history, location, currentUser) => {
  if (currentUser) {
    let redirectUrl = null

    const queryParams = new URLSearchParams(location.search)
    if (queryParams.has('de')) {
      redirectUrl = queryParams.get('de')
    } else if (currentUser.isAdmin) {
      redirectUrl = `/structures${location.search}`
    } else {
      redirectUrl = `/accueil${location.search}`
    }
    history.push(redirectUrl)
  }
}
