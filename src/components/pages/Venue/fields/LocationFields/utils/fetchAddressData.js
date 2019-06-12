const fetchAddressData = async url => {
  const response = await fetch(url)

  if (response.status === 404) {
    const error = `adresse ou coordonnées invalides`
    return { error }
  }

  const json = await response.json()
  const data = json.features.map(f => ({
    address: f.properties.name,
    city: f.properties.city,
    id: f.properties.id,
    latitude: f.geometry.coordinates[1],
    longitude: f.geometry.coordinates[0],
    label: f.properties.label,
    postalCode: f.properties.postcode,
  }))

  return data
}

export default fetchAddressData
