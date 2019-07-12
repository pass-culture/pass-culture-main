import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, code) {
  return code || ''
}

const selectShowTypeByCode = createCachedSelector(
  state => state.data.showTypes,
  (state, code) => code,
  (showTypes, code) => (showTypes || []).find(showType => showType.code.toString() === code)
)(mapArgsToCacheKey)

export default selectShowTypeByCode
