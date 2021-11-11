import createCachedSelector from 're-reselect'

const selectShowTypeByCode = createCachedSelector(
  state => state.data.showTypes,
  (state, code) => code,
  (showTypes, code) => showTypes.find(showType => showType.code.toString() === code)
)((state, code) => code)

export default selectShowTypeByCode
