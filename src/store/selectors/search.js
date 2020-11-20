import createCachedSelector from 're-reselect'

export const searchSelector = createCachedSelector(
  (state, search) => search,

  search => Object.fromEntries(new URLSearchParams(search)) || {}
)((state, search) => search || '')
