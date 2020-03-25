import { connect } from 'react-redux'
import { selectCurrentUser } from '../../../../selectors/data/usersSelectors'

import ProfileForm from './ProfileForm'

export const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state)

  return {
    initialValues: {
      publicName: currentUser.publicName,
    },
  }
}

export default connect(mapStateToProps)(ProfileForm)
