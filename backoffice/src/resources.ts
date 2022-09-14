import { ProSearch } from './resources/Pro/ProSearch'
import { UserSearch } from './resources/PublicUsers/UserSearch'
import { RolesList } from './resources/Roles/RolesList'

type ResourceType = {
  name: string
  list?: () => JSX.Element
  view?: () => JSX.Element
  edit?: () => JSX.Element
  create?: () => JSX.Element
}

export const resources: ResourceType[] = [
  {
    name: '/public_users/search',
    list: UserSearch,
  },
  {
    name: '/pro/search',
    list: ProSearch,
  },
  {
    name: '/roles',
    list: RolesList,
  },
]
