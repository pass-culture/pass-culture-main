import get from 'lodash.get'
import { createSelector } from 'reselect'

import { musicOptions } from '../utils/edd'

const selectMusicOptions = createSelector(
  parentCode => parentCode,
  parentCode => {
    if (!parentCode) {
      return
    }
    const option = musicOptions.find(option => option.code === parentCode)
    return get(option, 'children')
  }
)

export default selectMusicOptions
