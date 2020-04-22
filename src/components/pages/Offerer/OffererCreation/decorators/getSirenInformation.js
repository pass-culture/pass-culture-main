export const getSirenInformation = async siren => {
  const sirenUrl = `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`

  const response = await fetch(sirenUrl)

  if (response.status === 404) return { error: 'SIREN invalide' }
  if (response.status !== 200) return { error: 'Service indisponible' }

  const unitéLégale = await response.json().then(body => body.unite_legale)

  return {
    address: unitéLégale.etablissement_siege.geo_l4,
    city: unitéLégale.etablissement_siege.libelle_commune,
    latitude: parseFloat(unitéLégale.etablissement_siege.latitude) || null,
    longitude: parseFloat(unitéLégale.etablissement_siege.longitude) || null,
    name: unitéLégale.denomination || unitéLégale.etablissement_siege.enseigne_1 || '',
    postalCode: unitéLégale.etablissement_siege.code_postal,
    ['siren']: unitéLégale.siren,
  }
}

export default getSirenInformation
