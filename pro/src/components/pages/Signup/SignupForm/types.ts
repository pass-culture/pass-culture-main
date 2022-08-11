export interface ISignupFormValues {
  email: string
  password: string
  firstName: string
  lastName: string
  phoneNumber: string
  contactOk: string
  siren: string
  legalUnitValues: {
    address: string
    city: string
    name: string
    postalCode: string
    siren: string
  }
}

export interface ISignupApiErrorResponse {
  email?: string
  password?: string
  firstName?: string
  lastName?: string
  phoneNumber?: string
  contactOk?: string
  siren?: string
  address?: string
  city?: string
  latitude?: string | null
  longitude?: string | null
  name?: string
  postalCode?: string
}
