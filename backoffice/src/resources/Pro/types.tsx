import { RaRecord } from 'react-admin'

export interface ProResourceAPI extends RaRecord {
  resourceType: ProTypeEnum
  id: number
  status: string
  payload: ProUser | Venue | Offerer
}

export interface ProUser {
  firstName: string
  lastName: string
  email: string
  phoneNumber: string
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
}

export function isVenue(obj: ProUser | Venue | Offerer): obj is Venue {
  return 'name' in obj && 'email' in obj && 'siret' in obj && 'permanent' in obj
}

export interface Offerer {
  name: string
  siren: string
}

export function isOfferer(obj: ProUser | Venue | Offerer): obj is Offerer {
  return 'name' in obj && 'siren' in obj
}

export enum ProTypeEnum {
  proUser = 'proUser',
  offerer = 'offerer',
  venue = 'venue',
}
