import { API_ENTREPRISE_BASE_URL, STATUS_ACTIVE } from './constants'
import type { IEntrepriseSiretData, IEntrepriseDataFail } from './types'


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
    if (
      data.etat_administratif !== STATUS_ACTIVE ||
      data.unite_legale.etat_administratif !== STATUS_ACTIVE
    ) {
      return { error: 'SIRET invalide' }
    }

    return {
      address: data.geo_l4,
      city: data.libelle_commune,
      latitude: parseFloat(data.latitude) || null,
      longitude: parseFloat(data.longitude) || null,
      name:
        data.enseigne_1 ||
        data.unite_legale.denomination ||
        `${data.unite_legale.prenom_1} ${data.unite_legale.nom}` ||
        '',
      postalCode: data.code_postal,
      siret: data.siret,
    }
  },
}
