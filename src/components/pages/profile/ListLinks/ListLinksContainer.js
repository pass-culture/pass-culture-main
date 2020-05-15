import { connect } from 'react-redux'

import { selectReadRecommendations } from '../../../../redux/selectors/data/readRecommendationsSelectors'
import ListLinks from './ListLinks'

const mapStateToProps = state => ({
  readRecommendations: selectReadRecommendations(state),
})

export default connect(mapStateToProps)(ListLinks)
