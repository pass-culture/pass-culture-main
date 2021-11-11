export const redirectLoggedUser = (history, currentUser) => {
  if (currentUser) {
    if (currentUser.isAdmin) {
      history.push('/structures')
    } else {
      history.push('/accueil')
    }
  }
}
