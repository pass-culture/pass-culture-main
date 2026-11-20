import { createStorageManager } from './storageManager'

/**
 * **IMPORTANT**: Always prefix keys with `PASS_CULTURE_` to identify them as ours.
 */
export enum SESSION_STORAGE_KEY {
  INDIVIDUAL_OFFERS_FILTER_CONFIG = 'PASS_CULTURE_INDIVIDUAL_OFFERS_FILTER_CONFIG',
  COLLECTIVE_OFFERS_FILTER_CONFIG = 'PASS_CULTURE_COLLECTIVE_OFFERS_FILTER_CONFIG',
  TEMPLATE_OFFERS_FILTER_CONFIG = 'PASS_CULTURE_TEMPLATE_OFFERS_FILTER_CONFIG',
}

export const sessionStorageManager =
  createStorageManager<SESSION_STORAGE_KEY>('sessionStorage')
