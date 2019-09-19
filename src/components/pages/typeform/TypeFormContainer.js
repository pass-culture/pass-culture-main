import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'
import { selectCurrentUser } from 'with-react-redux-login'

import TypeForm from './TypeForm'
import { withRequiredLogin } from '../../hocs'

export const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state)
  const { needsToFillCulturalSurvey } = currentUser || {}
  return { needsToFillCulturalSurvey }
}

export const mapDispatchToProps = dispatch => ({
  flagUserHasFilledTypeform: uniqId => {
    const config = {
      apiPath: '/users/current',
      body: {
        culturalSurveyId: uniqId,
        needsToFillCulturalSurvey: false,
      },
      isMergingDatum: true,
      method: 'PATCH',
    }
    dispatch(requestData(config))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(TypeForm)
