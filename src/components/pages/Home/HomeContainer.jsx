import { connect } from 'react-redux'

import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'

import Home from './Home'

export function mapStateToProps(state) {
  return {
    isNewHomepageActive: selectIsFeatureActive(state, 'PRO_HOMEPAGE'),
  }
}

export default connect(mapStateToProps)(Home)
