import queryString from 'query-string'
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import * as typeformEmbed from '@typeform/embed'
import uuid from 'uuid/v1'

import { TYPEFORM_URL_CULTURAL_PRACTICES_POLL } from '../../../utils/config'

const buildTypeformURLWithHiddenFields = userId => {
  const search = queryString.stringify({ userId })
  const url = `${TYPEFORM_URL_CULTURAL_PRACTICES_POLL}?${search}`
  return url
}

class Typeform extends PureComponent {
  constructor(props) {
    super(props)
    this.typeFormContainer = React.createRef()
    this.uniqId = uuid()
    this.typeformUrl = buildTypeformURLWithHiddenFields(this.uniqId)
  }

  componentDidMount() {
    const { needsToFillCulturalSurvey } = this.props

    if (needsToFillCulturalSurvey) {
      this.displayEmbededTypeform()
    }
  }

  displayEmbededTypeform() {
    typeformEmbed.makeWidget(this.typeFormContainer.current, this.typeformUrl, {
      hideFooter: true,
      hideHeaders: true,
      onSubmit: this.onSubmitTypeForm,
      opacity: 100,
    })
  }

  onSubmitTypeForm = () => {
    const { flagUserHasFilledTypeform } = this.props
    flagUserHasFilledTypeform(this.uniqId, this.handleRequestSuccess)
  }

  handleRequestSuccess = () => {
    const { history } = this.props
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

Typeform.defaultProps = {
  needsToFillCulturalSurvey: true,
}

Typeform.propTypes = {
  flagUserHasFilledTypeform: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  needsToFillCulturalSurvey: PropTypes.bool,
}

export default Typeform
