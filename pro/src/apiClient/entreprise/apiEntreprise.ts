import { ApiError } from 'apiClient/entreprise/helpers'

import { API_ENTREPRISE_BASE_URL } from './constants'
import type {
  IEntrepriseApiJson,
  IEntrepriseSirenData,
  IEntrepriseSiretData,
} from './types'

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
  getSiretData: async (siret: string): Promise<IEntrepriseSiretData> => {
    const response = await handleApiError(
      await fetch(`${API_ENTREPRISE_BASE_URL}/etablissements/${siret}`)
    )
    const data = response.etablissement

    // https://www.sirene.fr/sirene/public/variable/statutDiffusionUniteLegale
    if (data.statut_diffusion == 'N') {
      throw new Error('Ce SIRET est masqué sur le répertoire de l’INSEE.')
    }

    const latitude =
      data.latitude || data.unite_legale.etablissement_siege.latitude
    const longitude =
      data.longitude || data.unite_legale.etablissement_siege.longitude
    return {
      address:
        data.geo_l4 ||
        data.unite_legale.etablissement_siege.geo_l4 ||
        data.unite_legale.etablissement_siege.geo_adresse,
      city: data.libelle_commune,
      latitude: latitude !== null ? parseFloat(latitude) : null,
      longitude: longitude !== null ? parseFloat(longitude) : null,
      name:
        data.enseigne_1 ||
        data.unite_legale.denomination ||
        `${data.unite_legale.prenom_1} ${data.unite_legale.nom}` ||
        '',
      postalCode: data.code_postal,
      siret: data.siret,
      companyStatus: data.etat_administratif,
      legalUnitStatus: data.unite_legale.etat_administratif,
    }
  },

  getSirenData: async (siren: string): Promise<IEntrepriseSirenData> => {
    const response = await handleApiError(
      await fetch(`${API_ENTREPRISE_BASE_URL}/unites_legales/${siren}`)
    )

    const legalUnit = response.unite_legale

    // https://www.sirene.fr/sirene/public/variable/statutDiffusionUniteLegale
    if (legalUnit.statut_diffusion == 'N') {
      throw new Error('Ce SIREN est masqué sur le répertoire de l’INSEE.')
    }

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
