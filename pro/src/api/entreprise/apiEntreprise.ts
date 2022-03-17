import { API_ENTREPRISE_BASE_URL } from './constants'
import type { IEntrepriseData, IEntrepriseDataFail } from './types'

export default {
  getEntrepriseDataFromSiret: async (
    siret: string
  ): Promise<IEntrepriseData | IEntrepriseDataFail> => {
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
}
