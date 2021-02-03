export const redirectLoggedUser = (history, currentUser, isNewHomepageActive) => {
  if (currentUser) {
    history.push(isNewHomepageActive ? '/accueil' : '/structures')
  }
}
