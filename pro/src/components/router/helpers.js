export const redirectLoggedUser = (history, currentUser) => {
  if (currentUser) {
    if (currentUser.isAdmin) {
      history.push(`/structures${location.search}`)
    } else {
      history.push(`/accueil${location.search}`)
    }
  }
}
