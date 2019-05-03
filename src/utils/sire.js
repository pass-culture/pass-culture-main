import get from 'lodash.get'
import { removeWhitespaces } from 'react-final-form-utils'
import createCachedSelector from 're-reselect'

import capitalize from './capitalize'

export const SIRET = 'siret'
export const SIREN = 'siren'

export function formatSire(string) {
  const value = removeWhitespaces(string)
  if (!value) {
    return ''
  }

  if (isNaN(value)) {
    return string.slice(0, -1)
  }

  const siren = value.substring(0, 9)
  const nic = value.substring(9)
  const sirenWithThreeBatchesOfThreeNumbers = (
    siren.match(/.{1,3}/g) || []
  ).join(' ')
  return `${sirenWithThreeBatchesOfThreeNumbers} ${nic}`.trim()
}

function mapArgsToCacheKey(siretOrSiren, sireType) {
  return `${siretOrSiren || ''}/${sireType || ''}`
}

export const getSireInfo = createCachedSelector(
  siretOrSiren => siretOrSiren,
  (siretOrSiren, sireType) => sireType,
  async (siretOrSiren, sireType) => {
    if (!sireType) {
      throw Error('You need to specify a sireType')
    }

    if (!siretOrSiren) {
      return
    }

    const withoutWhiteSpacesSiretOrSiren = removeWhitespaces(siretOrSiren)

    const isNotValidSiret =
      sireType === SIRET && withoutWhiteSpacesSiretOrSiren.length !== 14
    if (isNotValidSiret) {
      if (withoutWhiteSpacesSiretOrSiren.length < 14) {
        const error = `${capitalize(sireType)} trop court`
        return { error }
      }
      if (withoutWhiteSpacesSiretOrSiren.length > 14) {
        const error = `${capitalize(sireType)} trop long`
        return { error }
      }
    }

    const isNotValidSiren =
      sireType === SIREN && withoutWhiteSpacesSiretOrSiren.length !== 9
    if (isNotValidSiren) {
      if (withoutWhiteSpacesSiretOrSiren.length < 9) {
        const error = `${capitalize(sireType)} trop court`
        return { error }
      }
      if (withoutWhiteSpacesSiretOrSiren.length > 9) {
        const error = `${capitalize(sireType)} trop long`
        return { error }
      }
    }

    try {
      const sireUrl = `https://sirene.entreprise.api.gouv.fr/v1/${sireType}/${siretOrSiren}`

      const response = await fetch(sireUrl)

      if (response.status === 404) {
        const error = `${capitalize(sireType)} invalide`
        return { error }
      }

      const body = await response.json()
      const dataPath = sireType === SIREN ? 'siege_social' : 'etablissement'
      const sire = get(body, `${dataPath}.${sireType}`)

      const values = {
        address: get(body, `${dataPath}.l4_normalisee`),
        city: get(body, `${dataPath}.libelle_commune`),
        latitude: parseFloat(get(body, `${dataPath}.latitude`)) || null,
        longitude: parseFloat(get(body, `${dataPath}.longitude`)) || null,
        name:
          get(body, `${dataPath}.l1_normalisee`) ||
          get(body, `${dataPath}.l1_declaree`) ||
          '',
        postalCode: get(body, `${dataPath}.code_postal`),
        [sireType]: sire,
        sire,
      }

      return { values }
    } catch (e) {
      const error = `Impossible de vérifier le ${capitalize(sireType)} saisi.`
      return { error }
    }
  }
)(mapArgsToCacheKey)
