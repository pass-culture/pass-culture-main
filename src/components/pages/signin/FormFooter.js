/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { FormFooterObject } from '../../../types'

const renderSubmitButton = cancel => (
  <button
    id="signin-submit-button"
    type="submit"
    disabled={cancel.disabled}
    className={`flex-1  ${cancel.className || ''}`}
  >
    <span className="is-block">{cancel.label}</span>
  </button>
)

const renderLinkButton = submit => (
  <Link
    id="signin-signup-button"
    to={submit.url}
    disabled={submit.disabled}
    className={`flex-1  ${submit.className || ''}`}
  >
    <span className="is-block">{submit.label}</span>
  </Link>
)

class FormFooter extends React.PureComponent {
  render() {
    const { cancel, className, submit } = this.props

    return (
      <footer
        className={`pc-final-form-footer dotted-top-2x-white py7 flex-0 flex-columns text-center items-center fs20 ${className}`}
      >
        {cancel && cancel.url && renderLinkButton(cancel)}
        <hr className="dotted-left-2x-white flex-0" />
        {submit && !submit.url && renderSubmitButton(submit)}
      </footer>
    )
  }
}

FormFooter.defaultProps = {
  cancel: null,
  className: '',
  submit: null,
}

FormFooter.propTypes = {
  cancel: FormFooterObject,
  className: PropTypes.string,
  submit: FormFooterObject,
}

export default FormFooter
