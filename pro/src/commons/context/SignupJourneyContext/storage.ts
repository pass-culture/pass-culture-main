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
  const offerer = localStorageManager.getJSON<Offerer>(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER
  )
  if (offerer === null) {
    throw new Error(RESTORE_ERRORS.NO_OFFERER_DATA_IN_STORAGE)
  }
  setOfferer(offerer)
  return offerer
}

export const tryRestoreInitialAddressFromStorage = (
  setInitialAddress: (initialAddress: InitialAddress) => void
): InitialAddress => {
  const initialAddress = localStorageManager.getJSON<InitialAddress>(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
  )
  if (initialAddress === null) {
    throw new Error(RESTORE_ERRORS.NO_INITIAL_ADDRESS_DATA_IN_STORAGE)
  }
  setInitialAddress(initialAddress)
  return initialAddress
}

export const tryRestoreActivityFromStorage = (
  setActivity: (offererData: ActivityContext) => void
): ActivityContext => {
  const activity = localStorageManager.getJSON<ActivityContext>(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY
  )
  if (activity === null) {
    throw new Error(RESTORE_ERRORS.NO_ACTIVITY_DATA_IN_STORAGE)
  }
  setActivity(activity)
  return activity
}

export const saveOffererToStorage = (offerer: Offerer) => {
  localStorageManager.setJSON(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER, offerer)
}

export const saveInitialAddressToStorage = (initialAddress: InitialAddress) => {
  localStorageManager.setJSON(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS,
    initialAddress
  )
}

export const saveActivityToStorage = (activity: ActivityContext) => {
  localStorageManager.setJSON(
    LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY,
    activity
  )
}

export const cleanInitialAddressStorage = () => {
  try {
    localStorageManager.removeItem(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
    )
  } catch {
    return
  }
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
