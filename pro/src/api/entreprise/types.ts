export interface IEntrepriseSiretData {
  address: string
  city: string
  latitude: number | null
  longitude: number | null
  name: string
  postalCode: string
  siret: string
}

export interface IEntrepriseDataFail {
  error: string
}
