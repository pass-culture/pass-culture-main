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
