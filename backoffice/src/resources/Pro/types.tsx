import { ValidationStatus } from '../../TypesFromApi'

export interface ProUser {
  firstName: string
  lastName: string
  email: string
  phoneNumber: string
  isActive: boolean
}

export function isProUser(obj: ProUser | Venue | Offerer): obj is ProUser {
  return (
    'firstName' in obj &&
    'lastName' in obj &&
    'email' in obj &&
    'phoneNumber' in obj
  )
}

export interface Venue {
  name: string
  email: string
  siret: string
  permanent: boolean
  validationStatus: ValidationStatus
  isActive: boolean
}

export function isVenue(obj: ProUser | Venue | Offerer): obj is Venue {
  return 'name' in obj && 'email' in obj && 'siret' in obj && 'permanent' in obj
}

export interface Offerer {
  name: string
  siren: string
  validationStatus: ValidationStatus
  isActive: boolean
}

export function isOfferer(obj: ProUser | Venue | Offerer): obj is Offerer {
  return 'name' in obj && 'siren' in obj
}

export enum ProTypeEnum {
  proUser = 'proUser',
  offerer = 'offerer',
  venue = 'venue',
}
