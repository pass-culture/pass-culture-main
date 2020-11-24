import { connect } from 'react-redux'
// import { requestData } from 'redux-saga-data'

import OfferForm from './OfferForm'

// const mapStateToProps = (state) => ({
//   // types: state.data.types
// })

const mapDispatchToProps = () => ({
  // loadType: () => dispatch(requestData({ apiPath: '/types' })),
})

export default connect(null, mapDispatchToProps)(OfferForm)
