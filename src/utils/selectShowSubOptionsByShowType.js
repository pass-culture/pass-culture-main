import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import { showOptions } from './edd'

const selectShowSubOptionsByShowType = createCachedSelector(
  showType => showType,
  showType => {
    if (!showType) {
      return
    }
    const parentCode = Number(showType)
    const option = showOptions.find(option => option.code === parentCode)
    return get(option, 'children')
  }
)((musicType = ' ') => musicType)

export default selectShowSubOptionsByShowType
