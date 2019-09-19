import createCachedSelector from 're-reselect'

export const selectUserOffererByOffererIdAndUserIdAndRightsType = createCachedSelector(
  state => state.data.userOfferers,
  (state, offererId) => offererId,
  (state, offererId, userId) => userId,
  (state, offererId, userId, rights) => rights,
  (userOfferers, offererId, userId, rights) => {
    return userOfferers.find(
      userOfferer =>
        userOfferer.offererId === offererId &&
        userOfferer.userId === userId &&
        userOfferer.rights === rights
    )
  }
)((state, offererId = '', userId = '', right = '') => `${offererId}/${userId}/${right}`)
