import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.users,
  (state, userId) => userId,
  (users, userId) => users.find(user => user.id === userId)
)((state, userId) => userId || '')
