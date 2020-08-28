import { DELETE_REQUESTS } from './actions'

export const deleteRequests = key => ({
  key,
  type: DELETE_REQUESTS,
})
