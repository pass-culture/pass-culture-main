import createCachedSelector from 're-reselect'

import { selectOffererById } from './offerer'

function mapArgsToKey(state, offererId, userId, right) {
  return `${offererId || ''}/${userId || ''}/${right || ''}`
}

export const selectUserOffererByOffererIdAndUserIdAndRightsType = createCachedSelector(
  selectOffererById,
  (state, offererId, userId) => userId,
  (state, offererId, userId, rightsType) => rightsType,
  (offerer, userId, rightsType) => {
    if (!offerer) {
      return
    }
    return offerer.UserOfferers.find(
      userOfferer =>
        userOfferer.userId === userId &&
        userOfferer.rights === `RightsType.${rightsType}`
    )
  }
)(mapArgsToKey)

export default selectUserOffererByOffererIdAndUserIdAndRightsType
