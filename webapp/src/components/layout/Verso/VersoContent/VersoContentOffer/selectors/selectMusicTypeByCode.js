import createCachedSelector from 're-reselect'

const selectMusicTypeByCode = createCachedSelector(
  state => state.data.musicTypes,
  (state, code) => code,
  (musicTypes, code) => musicTypes.find(musicType => musicType.code.toString() === code)
)((state, code) => code)

export default selectMusicTypeByCode
