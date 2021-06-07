import { connect } from 'react-redux'

import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'

import OfferForm from './OfferForm'

const mapStateToProps = state => ({
  isIsbnRequiredInLivreEditionEnabled: selectIsFeatureActive(
    state,
    'ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION'
  ),
})

export default connect(mapStateToProps)(OfferForm)
