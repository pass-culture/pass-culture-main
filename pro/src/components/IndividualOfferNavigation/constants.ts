import { type EnumType } from 'commons/custom_types/utils'

export const OFFER_WIZARD_STEP_IDS = {
  DETAILS: 'details',
  USEFUL_INFORMATIONS: 'pratiques',
  TARIFS: 'tarifs',
  STOCKS: 'stocks',
  SUMMARY: 'recapitulatif',
  CONFIRMATION: 'confirmation',
  BOOKINGS: 'reservations',
} as const
// eslint-disable-next-line no-redeclare, @typescript-eslint/naming-convention
export type OFFER_WIZARD_STEP_IDS = EnumType<typeof OFFER_WIZARD_STEP_IDS>
