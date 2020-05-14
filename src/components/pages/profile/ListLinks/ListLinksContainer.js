import { connect } from 'react-redux'

import ListLinks from './ListLinks'

const mapStateToProps = state => ({
  readRecommendations: state.data.readRecommendations,
})

export default connect(mapStateToProps)(ListLinks)
