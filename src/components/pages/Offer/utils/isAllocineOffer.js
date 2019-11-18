const isAllocineOffer = offer => {
  if (offer == null) {
    return false
  }

  const { lastProvider } = offer
  if (lastProvider === null) {
    return false
  }

  return lastProvider.name
    .toLowerCase()
    .replace('é', 'e')
    .includes('allocine')
}

export default isAllocineOffer
