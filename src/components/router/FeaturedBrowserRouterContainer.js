import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import FeaturedBrowserRouter from './FeaturedBrowserRouter'

const mapStateToProps = state => {
  const { features } = state.data
  return { features }
}

const mapDispatchToProps = dispatch => ({
  requestGetFeatures: () => dispatch(requestData({ apiPath: '/features' })),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(FeaturedBrowserRouter)
