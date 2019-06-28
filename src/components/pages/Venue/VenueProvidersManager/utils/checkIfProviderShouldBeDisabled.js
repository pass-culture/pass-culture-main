const checkIfProviderShouldBeDisabled = (venueProviders, provider) => {
  const matchingVenueProvider = venueProviders.find(venueProvider => venueProvider.providerId === provider.id)
  let disableOption = false

  if (matchingVenueProvider) {
    if (provider.requireProviderIdentifier === false) {
      disableOption = true
    }
  }
  return disableOption
}

export default checkIfProviderShouldBeDisabled
