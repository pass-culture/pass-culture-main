import createCachedSelector from 're-reselect'

import occasionsSelector from './occasions'

export default createCachedSelector(
  state => occasionsSelector(state),
  (state, occasionId) => occasionId,
  (occasions, occasionId) => {
    return occasions.find(o => o.id === occasionId)
  }
)((state, occasionId) => occasionId || '')
