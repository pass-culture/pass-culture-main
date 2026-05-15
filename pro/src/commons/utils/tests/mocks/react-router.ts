import type { Location } from 'react-router'

export const makeUseLocationReturn = (
  overrides: Partial<Location>
): Location => ({
  pathname: '',
  search: '',
  hash: '',
  state: null,
  key: 's',
  ...overrides,
})
