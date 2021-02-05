import { connect } from 'react-redux'

import TutorialDialog from 'components/layout/Tutorial/TutorialDialog'
import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import { hasSeenTutorial } from 'store/selectors/data/usersSelectors'

const mapStateToProps = state => {
  return {
    hasSeenTutorial: hasSeenTutorial(state),
    isFeatureActive: selectIsFeatureActive(state, 'PRO_TUTO'),
  }
}

export default connect(mapStateToProps)(TutorialDialog)
