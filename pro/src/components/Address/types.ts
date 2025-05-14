export interface Address {
  city: string
  latitude: number | null
  longitude: number | null
  postalCode: string
  street: string
  banId: string | null
  manuallySetAddress?: boolean
  inseeCode: string | null
}
