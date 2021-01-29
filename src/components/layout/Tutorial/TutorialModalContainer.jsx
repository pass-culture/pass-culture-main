import { connect } from 'react-redux'

import { closeModal, showModal } from 'store/reducers/modal'
import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import { hasSeenTutorial } from 'store/selectors/data/usersSelectors'

import TutorialModal from './TutorialModal'

const mapStateToProps = state => {
  return {
    hasSeenTutorial: hasSeenTutorial(state),
    isFeatureActive: selectIsFeatureActive(state, 'FeatureToggle.PRO_TUTO'),
  }
}
const mapDispatchToProps = dispatch => {
  return {
    openTutorial: modalContent => dispatch(showModal(modalContent)),
    closeTutorial: () => dispatch(closeModal()),
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(TutorialModal)
