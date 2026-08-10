import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { TargetAudienceObject } from './SimulatorContext'

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

export const saveTargetAudienceToStorage = (
  targetAudiences: TargetAudienceObject
) => {
  localStorageManager.setItem(
    LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER,
    JSON.stringify(targetAudiences)
  )
}

export const tryRestoreTargetAudienceFromStorage = (
  setTargetAudiences: (targetAudienceData: TargetAudienceObject) => void
): TargetAudienceObject | undefined => {
  const targetAudienceStoredData = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER
  )
  if (targetAudienceStoredData === null) {
    return
  }
  const targetAudiences = JSON.parse(
    targetAudienceStoredData
  ) as TargetAudienceObject
  setTargetAudiences(targetAudiences)
  return targetAudiences
}

export const resetSimulatorActivityAndTargetStorage = () => {
  try {
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SIMULATOR_ACTIVITY)
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER)
  } catch {
    return
  }
}

export const resetSimulatorSiretAndOpenToPublicStorage = () => {
  try {
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SIMULATOR_SIRET)
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SIMULATOR_OPEN_TO_PUBLIC)
  } catch {
    return
  }
}
