import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import * as typeformEmbed from '@typeform/embed'

class TypeForm extends PureComponent {
  constructor(props) {
    super(props)
    this.typeformElementContainer = null
  }

  componentDidMount() {
    const { typeformUrl } = this.props
    const container = this.typeformElementContainer
    // NOTE Typeform Documentation
    // https://developer.typeform.com/embed/modes/
    typeformEmbed.makeWidget(container, typeformUrl, {
      hideFooter: true,
      hideHeaders: true,
      onSubmit: this.onSubmitTypeForm,
      opacity: 100,
    })
  }

  onSubmitTypeForm = () => {
    const { flagUserHasFilledTypeform, uniqId } = this.props
    flagUserHasFilledTypeform(uniqId)
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
  typeformUrl: PropTypes.string.isRequired,
  uniqId: PropTypes.string.isRequired,
}

export default TypeForm
