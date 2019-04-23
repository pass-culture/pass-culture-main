import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import * as typeformEmbed from '@typeform/embed'

// TODO -> move to constants
const TYPEFORM_URL = 'https://passculture.typeform.com/to/T8rurj'

// Default values taken from official Typeform docs
// https://developer.typeform.com/embed/modes/
const TYPEFORM_OPTIONS = {
  autoClose: 5,
  autoOpen: false,
  hideFooter: true,
  hideHeaders: true,
  mode: 'popup',
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
    const container = this.typeformElementContainer
    typeformEmbed.makeWidget(container, TYPEFORM_URL, opts)
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
