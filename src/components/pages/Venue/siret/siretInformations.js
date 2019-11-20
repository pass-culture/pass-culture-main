import get from 'lodash.get'
import { removeWhitespaces } from 'react-final-form-utils'
import createCachedSelector from 're-reselect'

export const formatSiret = (string) => {
  const value = removeWhitespaces(string)

  if (!value) {
    return ''
  }

  if (isNaN(value)) {
    return string.slice(0, -1)
  }

  const siren = value.substring(0, 9)
  const nic = value.substring(9)
  const sirenWithThreeBatchesOfThreeNumbers = (siren.match(/.{1,3}/g) || []).join(' ')
  return `${sirenWithThreeBatchesOfThreeNumbers} ${nic}`.trim()
}

export const validateSiretSize = siret => {
  if (siret.length < 14) {
    return 'SIRET trop court'
  }
  else if (siret.length > 14) {
    return 'SIRET trop long'
  }
  return ''
}

export const getLocationInformationsFromSiret = async siret => {
  const siretUrl = `https://entreprise.data.gouv.fr/api/sirene/v1/siret/${siret}`

  const response = await fetch(siretUrl)

  if (response.status === 404) {
    const error = 'SIRET invalide'
    return { error }
  }

  const body = await response.json()

  return {
    address: get(body, `etablissement.l4_normalisee`),
    city: get(body, `etablissement.libelle_commune`),
    latitude: parseFloat(get(body, `etablissement.latitude`)) || null,
    longitude: parseFloat(get(body, `etablissement.longitude`)) || null,
    name: get(body, `etablissement.l1_normalisee`) || get(body, `etablissement.l1_declaree`) || '',
    postalCode: get(body, `etablissement.code_postal`),
    ["siret"]: get(body, `etablissement.siret`),
    sire: get(body, `etablissement.siret`),
  }
}

const mapArgsToCacheKey = (siret) => siret || ''

export const getSiretInformations = createCachedSelector(
  siret => siret,
  async (siret) => {
    if (siret === '' || !siret) {
      return {
        values: {
          address: '',
          city:'',
          latitude: null,
          longitude: null,
          name: '',
          postalCode: '',
          sire: '',
          siret: '',
        }
      }
    }

    const siretWithoutWhiteSpaces = removeWhitespaces(siret)

    const error = validateSiretSize(siretWithoutWhiteSpaces)
    if (error) {
      return {error}
    }

    try {
      const values = await getLocationInformationsFromSiret(siretWithoutWhiteSpaces)
      return { values }
    } catch (e) {
      const error = 'Impossible de vérifier le SIRET saisi.'
      return { error }
    }
  }
)(mapArgsToCacheKey)
