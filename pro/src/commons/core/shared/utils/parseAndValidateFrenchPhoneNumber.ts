import { E164Number, parsePhoneNumberFromString } from 'libphonenumber-js'

import {
  FRENCH_PACIFIC_DOM_PHONE_REGION,
  GUADELOUPE_PHONE_REGION,
  GUYUANE_PHONE_REGION,
  MARTINIQUE_PHONE_REGION,
} from './phoneIndicativeByRegion'

const prefixRegionDict: { [key: string]: string } = {
  // La Réunion, Mayotte et autres territoires de l’Océan Indien
  '639': FRENCH_PACIFIC_DOM_PHONE_REGION,
  '692': FRENCH_PACIFIC_DOM_PHONE_REGION,
  '693': FRENCH_PACIFIC_DOM_PHONE_REGION,
  '262': FRENCH_PACIFIC_DOM_PHONE_REGION,
  // Guadeloupe, Saint-Martin et Saint-Barthélemy
  '690': GUADELOUPE_PHONE_REGION,
  '691': GUADELOUPE_PHONE_REGION,
  '590': GUADELOUPE_PHONE_REGION,
  // Guyane
  '694': GUYUANE_PHONE_REGION,
  '594': GUYUANE_PHONE_REGION,
  // Martinique
  '696': MARTINIQUE_PHONE_REGION,
  '697': MARTINIQUE_PHONE_REGION,
  '596': MARTINIQUE_PHONE_REGION,
}

export const parseAndValidateFrenchPhoneNumber = (phoneNumber: string) => {
  const defaultParsing = parsePhoneNumberFromString(phoneNumber, 'FR')
  if (!defaultParsing) {
    throw 'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
  }
  const prefix = defaultParsing.nationalNumber.substring(0, 3)
  let phoneNumberFormated = defaultParsing.number

  // Dom-tom numbers
  if (Object.keys(prefixRegionDict).includes(prefix)) {
    phoneNumberFormated =
      `+${prefixRegionDict[prefix]}${defaultParsing.nationalNumber}` as E164Number
  }
  const parsedPhoneNumber = parsePhoneNumberFromString(phoneNumberFormated)
  if (!parsedPhoneNumber || !parsedPhoneNumber.isValid()) {
    throw 'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
  }
  return parsedPhoneNumber
}

export const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone) {
    return false
  }
  try {
    parseAndValidateFrenchPhoneNumber(phone)
  } catch {
    return false
  }
  return true
}
