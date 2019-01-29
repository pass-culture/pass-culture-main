import {
  FUTURE_OFFERER_CREATED_IN_SIGNUP_PAGE,
  OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN,
} from './offerers'

export const FUTURE_USER_WITH_UNREGISTERED_OFFERER = {
  email: 'pctest.pro93.cafe0@btmx.fr',
  firstName: 'PC Test Pro',
  lastName: '93 Café0',
  password: 'pctest.Pro93.cafe0',
  siren: FUTURE_OFFERER_CREATED_IN_SIGNUP_PAGE.siren,
}

export const FUTURE_USER_WITH_REGISTERED_OFFERER_USER = {
  email: 'pctest.pro93.cafe1@btmx.fr',
  firstName: 'PC Test Pro',
  lastName: '93 Café1',
  password: 'pctest.Pro93.cafe1',
  siren: OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN.siren,
}

export const ADMIN_0_USER = {
  email: 'pctest.admin93.0@btmx.fr',
  firstName: 'PC Test Admin',
  lastName: '93 0',
  password: 'pctest.Admin93.0',
}

export const REAL_VALIDATION_USER = {
  email: 'pctest.pro93.real-validation@btmx.fr',
  validationToken: 'AZERTY123',
}

export const VALIDATED_UNREGISTERED_OFFERER_USER = {
  email: 'pctest.pro93.has-validated-unregistered-offerer@btmx.fr',
  firstName: 'PC Test Pro',
  lastName: '93 HVUO',
  password: 'pctest.Pro93.has-validated-unregistered-offerer',
  siren: OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN.siren,
}
