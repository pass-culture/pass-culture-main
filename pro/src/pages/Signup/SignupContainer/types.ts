export interface SignupFormValues {
  email: string
  password: string
  firstName: string
  lastName: string
  phoneNumber: string
  contactOk: boolean
}

export interface SignupApiErrorResponse {
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
