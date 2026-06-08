import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1/new'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { TargetCustomerObject } from './SimulatorContext'

export const saveSiretToStorage = (siret: string) => {
  localStorageManager.setItem(LOCAL_STORAGE_KEY.SIMULATOR_SIRET, siret)
}

export const tryRestoreSiretFromStorage = (
  setSiret: (siret: string) => void
): string | undefined => {
  const siretStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SIMULATOR_SIRET
  )
  if (siretStoredData === null) {
    return
  }
  setSiret(siretStoredData)
  return siretStoredData
}

export const saveActivityToStorage = (
  activity: ActivityOpenToPublic | ActivityNotOpenToPublic
) => {
  localStorageManager.setItem(LOCAL_STORAGE_KEY.SIMULATOR_ACTIVITY, activity)
}

export const tryRestoreActivityFromStorage = (
  setActivity: (
    activity: ActivityOpenToPublic | ActivityNotOpenToPublic
  ) => void
): ActivityOpenToPublic | ActivityNotOpenToPublic | undefined => {
  const activityStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SIMULATOR_ACTIVITY
  )
  if (activityStoredData === null) {
    return
  }
  const activityStored = activityStoredData as
    | ActivityOpenToPublic
    | ActivityNotOpenToPublic
  setActivity(activityStored)
  return activityStored
}

export const saveOpenToPublicToStorage = (openToPublic: string) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.SIMULATOR_OPEN_TO_PUBLIC,
    openToPublic
  )
}

export const tryRestoreOpenToPublicFromStorage = (
  setOpenToPublic: (openToPublic: string) => void
): string | undefined => {
  const openToPublicStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SIMULATOR_OPEN_TO_PUBLIC
  )
  if (openToPublicStoredData === null) {
    return
  }
  setOpenToPublic(openToPublicStoredData)
  return openToPublicStoredData
}

export const saveTargetCustomerToStorage = (
  targetCustomer: TargetCustomerObject
) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER,
    JSON.stringify(targetCustomer)
  )
}

export const tryRestoreTargetCustomerFromStorage = (
  setTargetCustomer: (targetCustomerData: TargetCustomerObject) => void
): TargetCustomerObject | undefined => {
  const targetCustomerStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER
  )
  if (targetCustomerStoredData === null) {
    return
  }
  const targetCustomer = JSON.parse(
    targetCustomerStoredData
  ) as TargetCustomerObject
  setTargetCustomer(targetCustomer)
  return targetCustomer
}
