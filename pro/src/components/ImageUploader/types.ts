import { type EnumType } from 'commons/custom_types/utils'

/* istanbul ignore file: not needed */
export const UploaderModeEnum = {
  OFFER: 'offer',
  OFFER_COLLECTIVE: 'offer_collective',
  VENUE: 'venue',
} as const
// eslint-disable-next-line no-redeclare
export type UploaderModeEnum = EnumType<typeof UploaderModeEnum>
