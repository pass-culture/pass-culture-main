export const redirectLoggedUser = (history, currentUser, isNewHomepageActive) => {
  if (currentUser) {
    if (currentUser.isAdmin) {
      history.push('/structures')
    } else {
      history.push(isNewHomepageActive ? '/accueil' : '/structures')
    }
  }
}
