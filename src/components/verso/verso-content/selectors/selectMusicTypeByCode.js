import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, code) {
  return code || ''
}

export const selectMusicTypeByCode = createCachedSelector(
  state => state.data.musicTypes,
  (state, code) => code,
  (musicTypes, code) =>
    (musicTypes || []).find(musicType => musicType.code.toString() === code)
)(mapArgsToCacheKey)

export default selectMusicTypeByCode
