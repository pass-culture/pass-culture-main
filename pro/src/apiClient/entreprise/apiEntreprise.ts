import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'

import { API_ENTREPRISE_BASE_URL } from './constants'
import type { IEntrepriseApiJson, IEntrepriseSiretData } from './types'

const handleApiError = async (
  response: Response,
  method: ApiRequestOptions['method'],
  url: string
): Promise<IEntrepriseApiJson> => {
  if (!response.ok) {
    throw new ApiError(
      { method, url },
      response,
      `Échec de la requête ${response.url}, code: ${response.status}`
    )
  }

  return (await response.json()) as IEntrepriseApiJson
}

export default {
  getSiretData: async (siret: string): Promise<IEntrepriseSiretData> => {
    const url = `${API_ENTREPRISE_BASE_URL}/etablissements/${siret}`
    const response = await handleApiError(await fetch(url), 'GET', url)
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
}
