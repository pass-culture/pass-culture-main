export const redirectLoggedUser = (history, currentUser) => {
  if (currentUser) {
    history.push(currentUser.hasPhysicalVenues ? '/offres' : '/structures')
  }
}
