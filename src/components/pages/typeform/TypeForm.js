import queryString from 'query-string'
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router-dom'
import * as typeformEmbed from '@typeform/embed'
import uuid from 'uuid/v1'

import { TYPEFORM_URL_CULTURAL_PRACTICES_POLL } from '../../../utils/config'

const buildTypeformURLWithHiddenFields = userId => {
  const search = queryString.stringify({ userId })
  const url = `${TYPEFORM_URL_CULTURAL_PRACTICES_POLL}?${search}`
  return url
}

class TypeForm extends PureComponent {
  constructor(props) {
    super(props)
    this.typeformElementContainer = null
    this.uniqId = uuid()
    this.typeformUrl = buildTypeformURLWithHiddenFields(this.uniqId)
  }

  componentDidMount() {
    const { needsToFillCulturalSurvey } = this.props
    if (!needsToFillCulturalSurvey) return
    const container = this.typeformElementContainer
    // NOTE Typeform Documentation
    // https://developer.typeform.com/embed/modes/
    typeformEmbed.makeWidget(container, this.typeformUrl, {
      hideFooter: true,
      hideHeaders: true,
      onSubmit: this.onSubmitTypeForm,
      opacity: 100,
    })
  }

  onSubmitTypeForm = () => {
    const { flagUserHasFilledTypeform } = this.props
    flagUserHasFilledTypeform(this.uniqId)
  }

  divRef = elt => {
    this.typeformElementContainer = elt
  }

  render() {
    const { needsToFillCulturalSurvey } = this.props
    if (!needsToFillCulturalSurvey) return <Redirect to="/decouverte" />
    return (<div
      className="is-overlay react-embed-typeform-container"
      ref={this.divRef}
            />)
  }
}

TypeForm.defaultProps = {
  needsToFillCulturalSurvey: true,
}

TypeForm.propTypes = {
  flagUserHasFilledTypeform: PropTypes.func.isRequired,
  needsToFillCulturalSurvey: PropTypes.bool,
}

export default TypeForm
