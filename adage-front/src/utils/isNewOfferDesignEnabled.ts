import { ENABLE_NEW_OFFER_DESIGN } from './config'

export const isNewOfferDesignEnabled = (): boolean =>
  ENABLE_NEW_OFFER_DESIGN === 'true'
