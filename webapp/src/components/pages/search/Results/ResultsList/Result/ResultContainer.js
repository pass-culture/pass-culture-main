import { connect } from 'react-redux'
import Result from './Result'
import { selectSearchGroupBySearchResult } from '../../../../../../redux/selectors/data/categoriesSelectors'

const mapStateToProps = (state, ownProps) => {
  const { result } = ownProps
  const { offer } = result
  const searchGroup = selectSearchGroupBySearchResult(state, offer)
  const searchGroupLabel = searchGroup ? searchGroup.value : ''

  return {
    searchGroupLabel,
  }
}

export default connect(mapStateToProps)(Result)
