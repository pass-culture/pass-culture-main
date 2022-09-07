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
