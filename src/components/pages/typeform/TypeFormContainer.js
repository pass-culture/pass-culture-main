import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'
import { selectCurrentUser } from 'with-react-redux-login'

import TypeForm from './TypeForm'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import moment from 'moment'

export const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state)
  const { needsToFillCulturalSurvey } = currentUser || {}
  return { needsToFillCulturalSurvey }
}

export const mapDispatchToProps = dispatch => ({
  flagUserHasFilledTypeForm: id => {
    const todayInUtc = moment().utc().format()

    dispatch(
      requestData({
        apiPath: '/users/current',
        body: {
          culturalSurveyId: id,
          culturalSurveyFilledDate: todayInUtc,
          needsToFillCulturalSurvey: false,
        },
        isMergingDatum: true,
        method: 'PATCH',
      }))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(TypeForm)
