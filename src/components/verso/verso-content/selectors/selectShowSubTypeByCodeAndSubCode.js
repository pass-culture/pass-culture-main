import createCachedSelector from 're-reselect'

import { selectShowTypeByCode } from './selectShowTypeByCode'

function mapArgsToCacheKey(state, code, subCode) {
  return `${code || ''}/${subCode || ''}`
}

export const selectShowSubTypeByCodeAndSubCode = createCachedSelector(
  selectShowTypeByCode,
  (state, code, subCode) => subCode,
  (showType, subCode) => {
    if (!showType) {
      return undefined
    }
    return showType.children.find(
      showSubType => showSubType.code.toString() === subCode
    )
  }
)(mapArgsToCacheKey)

export default selectShowSubTypeByCodeAndSubCode
