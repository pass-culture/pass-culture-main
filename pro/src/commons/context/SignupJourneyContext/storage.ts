import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type {
  ActivityContext,
  InitialAddress,
  Offerer,
} from './SignupJourneyContext'

export const RESTORE_ERRORS = {
  NO_OFFERER_DATA_IN_STORAGE: 'NO_OFFERER_DATA_IN_STORAGE',
  NO_INITIAL_ADDRESS_DATA_IN_STORAGE: 'NO_INITIAL_ADDRESS_DATA_IN_STORAGE',
  NO_ACTIVITY_DATA_IN_STORAGE: 'NO_ACTIVITY_DATA_IN_STORAGE',
}

export const tryRestoreOffererFromStorage = (
  setOfferer: (offererData: Offerer) => void
): Offerer => {
  const offererStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER
  )
  if (offererStoredData === null) {
    throw new Error(RESTORE_ERRORS.NO_OFFERER_DATA_IN_STORAGE)
  }
  const offerer = JSON.parse(offererStoredData) as Offerer
  setOfferer(offerer)
  return offerer
}

export const tryRestoreInitialAddressFromStorage = (
  setInitialAddress: (initialAddress: InitialAddress) => void
): InitialAddress => {
  const initialAddressStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
  )
  if (initialAddressStoredData === null) {
    throw new Error(RESTORE_ERRORS.NO_INITIAL_ADDRESS_DATA_IN_STORAGE)
  }
  const initialAddress = JSON.parse(initialAddressStoredData) as InitialAddress
  setInitialAddress(initialAddress)
  return initialAddress
}

export const tryRestoreActivityFromStorage = (
  setActivity: (offererData: ActivityContext) => void
): ActivityContext => {
  const activityStored = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY
  )
  if (activityStored === null) {
    throw new Error(RESTORE_ERRORS.NO_ACTIVITY_DATA_IN_STORAGE)
  }
  const activity = JSON.parse(activityStored) as ActivityContext
  setActivity(activity)
  return activity
}

export const saveOffererToStorage = (offerer: Offerer) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
    JSON.stringify(offerer)
  )
}

export const saveInitialAddressToStorage = (initialAddress: InitialAddress) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS,
    JSON.stringify(initialAddress)
  )
}

export const saveActivityToStorage = (activity: ActivityContext) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY,
    JSON.stringify(activity)
  )
}

export const cleanSignupJourneyStorage = () => {
  try {
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER)
    localStorageManager.removeItem(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
    )
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY)
  } catch {
    return
  }
}
