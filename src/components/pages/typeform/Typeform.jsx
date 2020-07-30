import queryString from 'query-string'
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import * as typeformEmbed from '@typeform/embed'
import uuid from 'uuid/v1'
import moment from 'moment'

import { TYPEFORM_URL_CULTURAL_PRACTICES_POLL } from '../../../utils/config'

const buildTypeformURLWithHiddenFields = userId => {
  const search = queryString.stringify({ userId })
  const url = `${TYPEFORM_URL_CULTURAL_PRACTICES_POLL}?${search}`
  return url
}

class Typeform extends PureComponent {
  constructor() {
    super()
    this.typeFormContainer = React.createRef()
    this.uniqId = uuid()
    this.typeformUrl = buildTypeformURLWithHiddenFields(this.uniqId)
  }

  componentDidMount() {
    this.displayEmbededTypeform()
  }

  displayEmbededTypeform() {
    typeformEmbed.makeWidget(this.typeFormContainer.current, this.typeformUrl, {
      hideFooter: true,
      hideHeaders: true,
      onSubmit: this.onSubmitTypeForm,
      opacity: 100,
    })
  }

  flagUserHasFilledTypeform = () => {
    const { updateCurrentUser } = this.props
    const todayInUtc = moment()
      .utc()
      .format()

    return updateCurrentUser({
      culturalSurveyId: this.uniqId,
      culturalSurveyFilledDate: todayInUtc,
      needsToFillCulturalSurvey: false,
    })
  }

  onSubmitTypeForm = async () => {
    const { history } = this.props
    await this.flagUserHasFilledTypeform()
    history.push('/bienvenue')
  }

  render() {
    return (
      <div
        className="is-overlay react-embed-typeform-container"
        ref={this.typeFormContainer}
      />
    )
  }
}

Typeform.propTypes = {
  history: PropTypes.shape().isRequired,
  updateCurrentUser: PropTypes.func.isRequired,
}

export default Typeform
