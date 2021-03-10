import queryString from 'query-string'
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import * as typeformEmbed from '@typeform/embed'
import moment from 'moment'
import uuid from 'uuid/v1'

import { TYPEFORM_URL_CULTURAL_PRACTICES_POLL } from '../../../utils/config'

class Typeform extends PureComponent {
  constructor(props) {
    super(props)
    this.typeformRef = React.createRef()
    this.culturalSurveyId = uuid()
  }

  componentDidMount() {
    this.displayEmbeddedTypeform()
  }

  displayEmbeddedTypeform = () => {
    const queryParams = queryString.stringify({
      userId: this.culturalSurveyId, // legacy issue : the query param userId is not the actual `user.id`
      userPk: this.props.userId,
    })
    const typeformUrl = `${TYPEFORM_URL_CULTURAL_PRACTICES_POLL}?${queryParams}`
    const widgetOptions = {
      hideFooter: true,
      hideHeaders: true,
      onSubmit: this.onSubmitTypeform,
      opacity: 100,
    }
    typeformEmbed.makeWidget(this.typeformRef.current, typeformUrl, widgetOptions)
  }

  onSubmitTypeform = async () => {
    const todayInUtc = moment().utc().format()
    await this.props.updateCurrentUser({
      culturalSurveyId: this.culturalSurveyId,
      culturalSurveyFilledDate: todayInUtc,
      needsToFillCulturalSurvey: false,
    })
    this.props.history.push('/bienvenue')
  }

  render() {
    return (
      <div
        className="is-overlay react-embed-typeform-container"
        ref={this.typeformRef}
      />
    )
  }
}

Typeform.propTypes = {
  history: PropTypes.shape().isRequired,
  updateCurrentUser: PropTypes.func.isRequired,
  userId: PropTypes.number.isRequired,
}

export default Typeform
