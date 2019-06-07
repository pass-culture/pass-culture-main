import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import TypeForm from './TypeForm'
import {
  selectCurrentUser,
  withRedirectToSigninOrTypeformAfterLogin,
} from '../../hocs'

const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state) || false
  const { hasFilledCulturalSurvey } = currentUser || {}
  return { hasFilledCulturalSurvey }
}

const mapDispatchToProps = dispatch => ({
  flagUserHasFilledTypeform: () => {
    const config = {
      apiPath: '/users/current',
      body: { hasFilledCulturalSurvey: true },
      isMergingDatum: true,
      method: 'PATCH',
    }
    dispatch(requestData(config))
  },
})

export default compose(
  withRedirectToSigninOrTypeformAfterLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(TypeForm)
