/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'

import { isFeatureActive } from 'store/features/selectors'

import StockItem from './StockItem'

const mapStateToProps = state => ({
  isActivationCodesEnabled: isFeatureActive(state, 'ENABLE_ACTIVATION_CODES'),
})

export default connect(mapStateToProps)(StockItem)
