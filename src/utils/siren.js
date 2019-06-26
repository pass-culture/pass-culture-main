import get from 'lodash.get'
import { removeWhitespaces } from 'react-final-form-utils'
import createCachedSelector from 're-reselect'

import capitalize from './capitalize'

export const SIRET = 'siret'
export const SIREN = 'siren'

export function formatSirenOrSiret(string) {
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

function mapArgsToCacheKey(sirenOrSiret, type) {
  return `${sirenOrSiret || ''}/${type || ''}`
}

export const getSirenOrSiretInfo = createCachedSelector(
  sirenOrSiret => sirenOrSiret,
  (sirenOrSiret, type) => type,
  async (sirenOrSiret, type) => {
    if (!type) {
      throw Error(`You need to specify a type : ${SIREN} or ${SIRET}`)
    }

    if (!sirenOrSiret) {
      return
    }

    const withoutWhiteSpacesSiretOrSiren = removeWhitespaces(sirenOrSiret)

    const isNotValidSiret =
      type === SIRET && withoutWhiteSpacesSiretOrSiren.length !== 14
    if (isNotValidSiret) {
      if (withoutWhiteSpacesSiretOrSiren.length < 14) {
        const error = `${capitalize(type)} trop court`
        return { error }
      }
      if (withoutWhiteSpacesSiretOrSiren.length > 14) {
        const error = `${capitalize(type)} trop long`
        return { error }
      }
    }

    const isNotValidSiren =
      type === SIREN && withoutWhiteSpacesSiretOrSiren.length !== 9
    if (isNotValidSiren) {
      if (withoutWhiteSpacesSiretOrSiren.length < 9) {
        const error = `${capitalize(type)} trop court`
        return { error }
      }
      if (withoutWhiteSpacesSiretOrSiren.length > 9) {
        const error = `${capitalize(type)} trop long`
        return { error }
      }
    }

    try {
      const sireneUrl = `https://sirene.entreprise.api.gouv.fr/v1/${type}/${withoutWhiteSpacesSiretOrSiren}`

      const response = await fetch(sireneUrl)

      if (response.status === 404) {
        const error = `${capitalize(type)} invalide`
        return { error }
      }

      const body = await response.json()
      const dataPath = type === SIREN ? 'siege_social' : 'etablissement'

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
        [type]: get(body, `${dataPath}.${type}`),
        sire: get(body, `${dataPath}.${type}`),
      }

      return { values }
    } catch (e) {
      const error = `Impossible de vérifier le ${capitalize(type)} saisi.`
      return { error }
    }
  }
)(mapArgsToCacheKey)
