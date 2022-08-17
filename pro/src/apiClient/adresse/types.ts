export interface IFeatureAdresseApi {
  geometry: {
    coordinates: [number, number]
  }
  properties: {
    name: string
    city: string
    id: string
    label: string
    postCode: string
  }
}

export interface IAdresseApiJson {
  type: string
  version: string
  features: Array<IFeatureAdresseApi>
}

export interface IAdresseData {
  address: string
  city: string
  id: string
  latitude: number
  longitude: number
  label: string
  postalCode: string
}
