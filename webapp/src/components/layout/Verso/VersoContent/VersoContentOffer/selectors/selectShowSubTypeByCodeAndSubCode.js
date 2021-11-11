import createCachedSelector from 're-reselect'

import selectShowTypeByCode from './selectShowTypeByCode'

const selectShowSubTypeByCodeAndSubCode = createCachedSelector(
  selectShowTypeByCode,
  (state, code, subCode) => subCode,
  (showType, subCode) => {
    if (!showType) {
      return undefined
    }

    return showType.children.find(showSubType => showSubType.code.toString() === subCode)
  }
)((state, code, subCode) => `${code || ''}/${subCode || ''}`)

export default selectShowSubTypeByCodeAndSubCode
