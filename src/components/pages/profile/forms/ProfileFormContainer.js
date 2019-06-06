import { connect } from 'react-redux'
import ProfileForm from './ProfileForm'

import { selectCurrentUser } from '../../../hocs'

export const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state)

  return {
    initialValues: {
      publicName: currentUser.publicName,
    },
  }
}

export default connect(mapStateToProps)(ProfileForm)
