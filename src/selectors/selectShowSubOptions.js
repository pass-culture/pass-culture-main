import get from 'lodash.get'
import { createSelector } from 'reselect'

import { showOptions } from '../utils/edd'

const selectShowSubOptions = createSelector(
  parentCode => parentCode,
  parentCode => {
    if (!parentCode) {
      return
    }
    const option = showOptions.find(option => option.code === parentCode)
    return get(option, 'children')
  }
)

export default selectShowSubOptions
