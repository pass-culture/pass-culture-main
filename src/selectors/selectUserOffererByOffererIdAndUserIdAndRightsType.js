import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, offererId, userId, right) {
  return `${offererId || ''}/${userId || ''}/${right || ''}`
}

export const selectUserOffererByOffererIdAndUserIdAndRightsType = createCachedSelector(
  state => state.data.userOfferers,
  (state, offererId) => offererId,
  (state, offererId, userId) => userId,
  (state, offererId, userId, rightsType) => rightsType,
  (userOfferers, offererId, userId, rightsType) => {
    return userOfferers.find(
      userOfferer =>
        userOfferer.offererId === offererId &&
        userOfferer.userId === userId &&
        userOfferer.rights === `RightsType.${rightsType}`
    )
  }
)(mapArgsToCacheKey)

export default selectUserOffererByOffererIdAndUserIdAndRightsType
