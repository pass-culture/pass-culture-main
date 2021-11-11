import createCachedSelector from 're-reselect'

import selectMusicTypeByCode from './selectMusicTypeByCode'

const selectMusicSubTypeByCodeAndSubCode = createCachedSelector(
  selectMusicTypeByCode,
  (state, code, subCode) => subCode,
  (musicType, subCode) => {
    if (!musicType) {
      return undefined
    }

    return musicType.children.find(musicSubType => musicSubType.code.toString() === subCode)
  }
)((state, code, subCode) => `${code || ''}/${subCode || ''}`)

export default selectMusicSubTypeByCodeAndSubCode
