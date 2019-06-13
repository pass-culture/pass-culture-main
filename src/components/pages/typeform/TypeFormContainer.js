import uuid from 'uuid/v1'
import queryString from 'query-string'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import TypeForm from './TypeForm'
import {
  selectCurrentUser,
  withRedirectToSigninOrTypeformAfterLogin,
} from '../../hocs'
import { TYPEFORM_URL_CULTURAL_PRACTICES_POLL } from '../../../utils/config'

const buildTypeformURLWithHiddenFields = userId => {
  const search = queryString.stringify({ userId })
  const url = `${TYPEFORM_URL_CULTURAL_PRACTICES_POLL}?${search}`
  return url
}

export const mapStateToProps = state => {
  const uniqId = uuid()
  const currentUser = selectCurrentUser(state)
  const typeformUrl = buildTypeformURLWithHiddenFields(uniqId)
  const { hasFilledCulturalSurvey } = currentUser || {}
  return { hasFilledCulturalSurvey, typeformUrl, uniqId }
}

export const mapDispatchToProps = dispatch => ({
  flagUserHasFilledTypeform: uniqId => {
    const config = {
      apiPath: '/users/current',
      body: {
        culturalSurveyId: uniqId,
        hasFilledCulturalSurvey: true,
      },
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
