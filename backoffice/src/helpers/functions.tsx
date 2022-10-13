import { PermissionsEnum } from '../resources/PublicUsers/types'

export const searchPermission = (
  permissions: PermissionsEnum[],
  permissionToFind: PermissionsEnum
) => {
  if (permissions) {
    const permissionFound = permissions.find(
      permission => permission === permissionToFind
    )
    return permissionFound ?? false
  }

  return false
}

export const uuid = () =>
  'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0,
      v = c == 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
