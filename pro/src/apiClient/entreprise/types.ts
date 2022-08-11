export interface IEntrepriseSiretData {
  address: string
  city: string
  latitude: number | null
  longitude: number | null
  name: string
  postalCode: string
  siret: string
  companyStatus: string
  legalUnitStatus: string
}

export interface IEntrepriseApiJson {
  unite_legale: {
    statut_diffusion: string
    prenom_1: string | null
    nom: string | null
    denomination: string | null
    etablissement_siege: {
      geo_adresse: string
      enseigne_1: string | null
      geo_l4: string
      libelle_commune: string
      latitude: string | null
      longitude: string | null
      code_postal: string
    }
    siren: string
  }
  etablissement: {
    statut_diffusion: string
    enseigne_1: string | null
    geo_l4: string
    libelle_commune: string
    latitude: string | null
    longitude: string | null
    code_postal: string
    siret: string
    unite_legale: {
      prenom_1: string | null
      nom: string | null
      denomination: string | null
      etat_administratif: string
      etablissement_siege: {
        geo_l4: string
        geo_adresse: string
        longitude: string
        latitude: string
      }
      siren: string
    }
    etat_administratif: string
  }
}
