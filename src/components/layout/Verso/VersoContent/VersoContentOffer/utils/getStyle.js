import selectMusicTypeByCode from '../selectors/selectMusicTypeByCode'
import selectMusicSubTypeByCodeAndSubCode from '../selectors/selectMusicSubTypeByCodeAndSubCode'
import selectShowTypeByCode from '../selectors/selectShowTypeByCode'
import selectShowSubTypeByCodeAndSubCode from '../selectors/selectShowSubTypeByCodeAndSubCode'

const getStyle = (state, extraData) => {
  if (extraData === undefined) return ''

  let style = ''
  let type = ''

  if (extraData.musicType) {
    const { musicSubType: musicSubCode, musicType: musicCode } = extraData
    const musicType = selectMusicTypeByCode(state, musicCode)
    const musicSubType = selectMusicSubTypeByCodeAndSubCode(state, musicCode, musicSubCode)

    if (musicType) {
      type = musicType.label
    }

    if (musicSubType) {
      style = ` / ${musicSubType.label}`
    }
  }

  if (extraData.showType) {
    const { showSubType: showSubCode, showType: showCode } = extraData
    const showType = selectShowTypeByCode(state, showCode)
    const showSubType = selectShowSubTypeByCodeAndSubCode(state, showCode, showSubCode)

    if (showType) {
      type = showType.label
    }

    if (showSubType) {
      style = ` / ${showSubType.label}`
    }
  }

  return `${type}${style}`
}

export default getStyle
