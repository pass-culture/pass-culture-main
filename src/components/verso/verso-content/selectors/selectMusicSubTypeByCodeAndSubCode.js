import createCachedSelector from 're-reselect'

import { selectMusicTypeByCode } from './selectMusicTypeByCode'

function mapArgsToCacheKey(state, code, subCode) {
  return `${code || ''}/${subCode || ''}`
}

export const selectMusicSubTypeByCodeAndSubCode = createCachedSelector(
  selectMusicTypeByCode,
  (state, code, subCode) => subCode,
  (musicType, subCode) => {
    if (!musicType) {
      return undefined
    }
    return musicType.children.find(
      musicSubType => musicSubType.code.toString() === subCode
    )
  }
)(mapArgsToCacheKey)

export default selectMusicSubTypeByCodeAndSubCode
