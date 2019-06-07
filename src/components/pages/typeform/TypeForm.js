import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import * as typeformEmbed from '@typeform/embed'

import { TYPEFORM_URL_CULTURAL_PRACTICES_POLL } from '../../../utils/config'

// Default values taken from official Typeform docs
// https://developer.typeform.com/embed/modes/
const TYPEFORM_OPTIONS = {
  hideFooter: true,
  hideHeaders: true,
  opacity: 100,
}

class TypeForm extends PureComponent {
  constructor(props) {
    super(props)
    this.typeformElementContainer = null
  }

  componentDidMount() {
    const opts = {
      ...TYPEFORM_OPTIONS,
      onSubmit: this.onSubmitTypeForm,
    }
    const url = TYPEFORM_URL_CULTURAL_PRACTICES_POLL
    const container = this.typeformElementContainer
    typeformEmbed.makeWidget(container, url, opts)
  }

  onSubmitTypeForm = () => {
    const { flagUserHasFilledTypeform } = this.props
    flagUserHasFilledTypeform()
  }

  render() {
    return (
      <div
        className="is-overlay react-embed-typeform-container"
        ref={elt => {
          this.typeformElementContainer = elt
        }}
      />
    )
  }
}

TypeForm.propTypes = {
  flagUserHasFilledTypeform: PropTypes.func.isRequired,
}

export default TypeForm
