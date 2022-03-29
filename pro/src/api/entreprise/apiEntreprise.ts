import { ApiError } from 'api/helpers'

import { API_ENTREPRISE_BASE_URL } from './constants'
import type {
  IEntrepriseSiretData,
  IEntrepriseSirenData,
  IEntrepriseDataFail,
} from './types'

interface IEntrepriseApiJson {
  unite_legale: {
    prenom_1: string | null
    nom: string | null
    denomination: string | null
    etablissement_siege: {
      enseigne_1: string | null
      geo_l4: string
      libelle_commune: string
      latitude: string | null
      longitude: string | null
      code_postal: string
    }
    siren: string
  }
}

const handleApiError = async (
  response: Response
): Promise<IEntrepriseApiJson> => {
  if (!response.ok) {
    throw new ApiError(
      response.status,
      await response.json(),
      `Échec de la requête ${response.url}, code: ${response.status}`
    )
  }

  return (await response.json()) as IEntrepriseApiJson
}

export default {
  getSiretData: async (
    siret: string
  ): Promise<IEntrepriseSiretData | IEntrepriseDataFail> => {
    const response = await fetch(
      `${API_ENTREPRISE_BASE_URL}/etablissements/${siret}`
    )

    if (response.status === 404) {
      return { error: 'SIRET invalide' }
    }

    const data = await response.json().then(body => body.etablissement)
    return {
      address: data.geo_l4,
      city: data.libelle_commune,
      latitude: parseFloat(data.latitude) || null,
      longitude: parseFloat(data.longitude) || null,
      name: data.enseigne_1 || data.unite_legale.denomination || '',
      postalCode: data.code_postal,
      siret: data.siret,
    }
  },
  getSirenData: async (
    siren: string
  ): Promise<IEntrepriseSirenData | IEntrepriseDataFail> => {
    const response = await handleApiError(
      await fetch(`${API_ENTREPRISE_BASE_URL}/unites_legales/${siren}`)
    )

    const legalUnit = response.unite_legale

    let name
    if (legalUnit.denomination) {
      name = legalUnit.denomination
    } else if (legalUnit.etablissement_siege.enseigne_1) {
      name = legalUnit.etablissement_siege.enseigne_1
    } else {
      name = `${legalUnit.prenom_1 || ''} ${legalUnit.nom || ''}`
    }

    const latitude = legalUnit.etablissement_siege.latitude
    const longitude = legalUnit.etablissement_siege.longitude

    return {
      address: legalUnit.etablissement_siege.geo_l4,
      city: legalUnit.etablissement_siege.libelle_commune,
      latitude: latitude ? parseFloat(latitude) : null,
      longitude: longitude ? parseFloat(longitude) : null,
      name,
      postalCode: legalUnit.etablissement_siege.code_postal,
      siren: legalUnit.siren,
    }
  },
}
