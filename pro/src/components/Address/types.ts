export interface Address {
  city: string
  latitude: number | null
  longitude: number | null
  postalCode: string
  street: string | null
  banId: string | null
  manuallySetAddress?: boolean
}
