const checkIfProviderShouldBeDisabled = (venueProviders, provider) => {
  const matchingVenueProvider = venueProviders.find(
    venueProvider => venueProvider.providerId === provider.id
  )

  return matchingVenueProvider !== undefined
}

export default checkIfProviderShouldBeDisabled
