// @docs : https://adresse.data.gouv.fr/outils/api-doc/adresse

export type FeaturePropertyType =
  | 'housenumber' // numéro « à la plaque »
  | 'street' // position « à la voie », placé approximativement au centre de celle-ci
  | 'locality' // lieu-dit
  | 'municipality' // numéro « à la commune »'

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
    citycode: string
    context: string
    district: string
    housenumber: string
    importance: number
    score: number
    street: string
    type: FeaturePropertyType
    x: number
    y: number
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
  inseeCode: string
  id: string
  latitude: number
  longitude: number
  label: string
  postalCode: string
}
