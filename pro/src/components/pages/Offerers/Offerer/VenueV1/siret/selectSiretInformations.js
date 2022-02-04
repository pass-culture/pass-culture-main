import createCachedSelector from 're-reselect'
import { removeWhitespaces } from 'react-final-form-utils'

export const validateSiretSize = siret => {
  if (siret.length < 14) {
    return 'SIRET trop court'
  } else if (siret.length > 14) {
    return 'SIRET trop long'
  }
  return ''
}

const getLocationInformationsFromSiret = async siret => {
  const siretUrl = `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`

  const response = await fetch(siretUrl)

  if (response.status === 404) {
    const error = 'SIRET invalide'
    return { error }
  }

  const établissement = await response.json().then(body => body.etablissement)

  return {
    address: établissement.geo_l4,
    city: établissement.libelle_commune,
    latitude: parseFloat(établissement.latitude) || null,
    longitude: parseFloat(établissement.longitude) || null,
    name:
      établissement.enseigne_1 || établissement.unite_legale.denomination || '',
    postalCode: établissement.code_postal,
    ['siret']: établissement.siret,
    sire: établissement.siret,
  }
}

const mapArgsToCacheKey = siret => siret || ''

export const getSiretInformations = createCachedSelector(
  siret => siret,
  async siret => {
    if (siret === '' || !siret) {
      return {
        values: {
          address: '',
          city: '',
          latitude: null,
          longitude: null,
          name: '',
          postalCode: '',
          sire: '',
          siret: '',
        },
      }
    }

    const siretWithoutWhiteSpaces = removeWhitespaces(siret)

    const error = validateSiretSize(siretWithoutWhiteSpaces)
    if (error) {
      return { error }
    }

    try {
      const values = await getLocationInformationsFromSiret(
        siretWithoutWhiteSpaces
      )
      return { values }
    } catch (e) {
      const error = 'Impossible de vérifier le SIRET saisi.'
      return { error }
    }
  }
)(mapArgsToCacheKey)
