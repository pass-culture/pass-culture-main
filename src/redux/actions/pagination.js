export const UPDATE_PAGE = 'UPDATE_PAGE'
export const UPDATE_SEED = 'UPDATE_SEED'
export const UPDATE_SEED_LAST_REQUEST_TIMESTAMP = 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP'

export const updatePage = (page) => ({
  page,
  type: UPDATE_PAGE,
})

export const updateSeed = (seed) => ({
  seed,
  type: UPDATE_SEED,
})

export const updateSeedLastRequestTimestamp = (seedLastRequestTimestamp) => ({
  seedLastRequestTimestamp,
  type: UPDATE_SEED_LAST_REQUEST_TIMESTAMP,
})
