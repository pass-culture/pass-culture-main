import { connect } from 'react-redux'

import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'

import StockItem from './StockItem'

const mapStateToProps = state => ({
  isActivationCodesEnabled: selectIsFeatureActive(state, 'ENABLE_ACTIVATION_CODES'),
})

export default connect(mapStateToProps)(StockItem)
