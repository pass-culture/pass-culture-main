import get from 'lodash.get'

export const getSirenInformation = async siren => {
  const sirenUrl = `https://entreprise.data.gouv.fr/api/sirene/v1/siren/${siren}`

  const response = await fetch(sirenUrl)

  if (response.status === 404) return { error: 'SIREN invalide' }
  if (response.status !== 200) return { error: 'Service indisponible' }

  const body = await response.json()

  return {
    address: get(body, `siege_social.l4_normalisee`),
    city: get(body, `siege_social.libelle_commune`),
    latitude: parseFloat(get(body, `siege_social.latitude`)) || null,
    longitude: parseFloat(get(body, `siege_social.longitude`)) || null,
    name: get(body, `siege_social.l1_normalisee`) || get(body, `siege_social.l1_declaree`) || '',
    postalCode: get(body, `siege_social.code_postal`),
    ['siren']: get(body, `siege_social.siren`),
  }
}

export default getSirenInformation
