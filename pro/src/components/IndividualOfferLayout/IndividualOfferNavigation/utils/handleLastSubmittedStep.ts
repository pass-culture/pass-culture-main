import { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { storageAvailable } from '@/commons/utils/storageAvailable'

// Deprecated - only for "Informations pratiques" step (e.g: IndividualOfferInformationsScreen)
// USEFUL_INFORMATION_SUBMITTED_${offerId}: 'true' | null
const LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED =
  'USEFUL_INFORMATION_SUBMITTED'
const getDeprecatedLocalStorageKeyName = (offerId: number | string) =>
  `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offerId}`

// New - includes all steps.
// individualOfferLastSubmittedStep_${offerId}: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.[STEP]
const LOCAL_INDIV_OFFER_LAST_SUBMITTED_STEP = 'individualOfferLastSubmittedStep'
export const getLocalStorageKeyName = (offerId: number | string) =>
  `${LOCAL_INDIV_OFFER_LAST_SUBMITTED_STEP}_${offerId}`

const getLastSubmittedStep = (
  offerId?: number | string
): INDIVIDUAL_OFFER_WIZARD_STEP_IDS | null => {
  // We can infer that in absence of offerId, the POST offer api
  // hasn't be called yet - so it's a draft offer.
  // User is at step one of individual offer creation,
  // but it hasn't be submitted yet.
  if (!offerId) {
    return null
  }

  if (storageAvailable('localStorage')) {
    // We check the existence of a more generic localStorage key to save
    // submitted steps - since we might need to remember this information
    // for any step of the individual offer creation process.
    const keyName = getLocalStorageKeyName(offerId)
    const lastSubmittedStep = localStorage.getItem(
      keyName
    ) as INDIVIDUAL_OFFER_WIZARD_STEP_IDS

    // We check the existence of the deprecated key,
    // which only helps remember that useful information has been submitted.
    const deprecatedKeyName = getDeprecatedLocalStorageKeyName(offerId)
    const deprecatedUsefulInformationSubmitted =
      localStorage.getItem(deprecatedKeyName)

    // If both keys exist, than the deprecated key can be cleaned up,
    // the most modern one is to be returned.
    // If only the deprecated key exists, it's because the user has
    // not submitted any step following INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
    // yet (and has used an older version of the app).
    if (lastSubmittedStep) {
      if (deprecatedUsefulInformationSubmitted) {
        localStorage.removeItem(deprecatedKeyName)
      }

      return lastSubmittedStep
    } else if (deprecatedUsefulInformationSubmitted) {
      return INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
    } else {
      return null
    }
  } else {
    return null
  }
}

const updateLocalStorageWithLastSubmittedStep = (
  offerId: number | string,
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
) => {
  if (storageAvailable('localStorage')) {
    const keyName = getLocalStorageKeyName(offerId)
    localStorage.setItem(keyName, step)
  }
}

// To be used when offer creation is completed.
const cleanLocalStorageAboutLastSubmittedStep = (offerId: number | string) => {
  if (storageAvailable('localStorage')) {
    const keyName = getLocalStorageKeyName(offerId)
    localStorage.removeItem(keyName)

    // Always cleanup the localStorage regarding the deprecated key at
    // this point.
    const deprecatedKeyName = getDeprecatedLocalStorageKeyName(offerId)
    localStorage.removeItem(deprecatedKeyName)
  }
}

export {
  getLastSubmittedStep,
  updateLocalStorageWithLastSubmittedStep,
  cleanLocalStorageAboutLastSubmittedStep,
}
