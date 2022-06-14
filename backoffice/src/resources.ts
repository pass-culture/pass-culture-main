import UserSearch from './resources/PublicUsers/UserSearch'

type ResourceType = {
  name: string
  list?: () => JSX.Element,
  edit?: () => JSX.Element,
  create?: () => JSX.Element,
  view?: () => JSX.Element,
}

export const resources: ResourceType[] = [
  {
    name: '/public_users/search',
    list: UserSearch,
  }
]
