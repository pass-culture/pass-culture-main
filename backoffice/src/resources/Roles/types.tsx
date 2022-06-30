import { Identifier, RaRecord } from 'react-admin'

export interface Permission extends RaRecord {
  id: Identifier
  category: string
  name: string
}

export interface Role extends RaRecord {
  id: Identifier
  name: string
  permissions: Permission[]
}

export interface RoleRequest {
  name: string
  permissionIds: number[]
}
