/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { FormFooterObject } from '../../../types'

const renderSubmitButton = obj => (
  <button
    type="submit"
    disabled={obj.disabled}
    className={`flex-1  ${obj.className || ''}`}
  >
    <span className="is-block">{obj.label}</span>
  </button>
)

const renderLinkButton = obj => (
  <Link
    to={obj.url}
    disabled={obj.disabled}
    className={`flex-1  ${obj.className || ''}`}
  >
    <span className="is-block">{obj.label}</span>
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
