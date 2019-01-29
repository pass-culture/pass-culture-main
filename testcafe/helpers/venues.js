import {
  OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN,
  OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN,
} from './offerers'

const latitude = '48.83638'
const longitude = '2.40027'
export const FUTURE_PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN = {
  address: 'RUE DES POILUS',
  anchor: '#a-herbert-marcuse-entreprise',
  city: 'Drancy',
  latitude,
  longitude,
  marker: `${latitude}-${longitude}`,
  name: 'Le lieu magique de type fussoir',
  postalCode: '93700',
  siret: `${OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN.siren}21111`,
}

export const FUTURE_PHYSICAL_VENUE_WITH_NO_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN = {
  address: '1 place du trocadéro',
  banAddress: '1 Place du Trocadero et du 11 Novembre 75016 Paris',
  city: 'Paris',
  comment: 'Test sans SIRET',
  latitude: '48.862923',
  longitude: '2.287896',
  name: 'Le lieu sympa de type sans siret',
  postalCode: '75016',
}

export const PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN = {
  address: OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN.address,
  city: OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN.city,
  latitude: '48.91678',
  longitude: '2.43846',
  name: 'Club Dorothy',
  postalCode: OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN.postalCode,
  siret: `${OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN.siren}11111`,
}
