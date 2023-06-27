export interface FeatureAdresseApi {
  geometry: {
    coordinates: [number, number]
  }
  properties: {
    name: string
    city: string
    id: string
    label: string
    postcode: string
  }
}

export interface AdresseApiJson {
  type: string
  version: string
  features: Array<FeatureAdresseApi>
}

export interface AdresseData {
  address: string
  city: string
  id: string
  latitude: number
  longitude: number
  label: string
  postalCode: string
}
