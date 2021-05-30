import { connect } from 'react-redux'

import { isFeatureActive } from 'store/features/selectors'

import StockItem from './StockItem'

const mapStateToProps = state => ({
  isActivationCodesEnabled: isFeatureActive(state, 'ENABLE_ACTIVATION_CODES'),
})

export default connect(mapStateToProps)(StockItem)
