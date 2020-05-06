export const checkIfSearchAround = (searchAround) => {
  return searchAround.place || searchAround.user ? 'oui' : 'non'
}
