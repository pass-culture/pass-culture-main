/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { FormFooterObject } from '../../types'

const renderSubmitButton = obj => {
  const props = {
    className: `flex-1 ${obj.className || ''}`,
    disabled: obj.disabled,
  }
  if (obj.id) props.id = obj.id
  return (
    <button
      type="submit"
      {...props}
    >
      <span className="is-block">{obj.label}</span>
    </button>
  )
}

const renderLinkButton = obj => {
  const props = {
    className: `flex-1 ${obj.className || ''}`,
    disabled: obj.disabled,
    to: obj.url,
  }
  if (obj.id) props.id = obj.id
  return (
    <Link {...props}>
      <span className="is-block">{obj.label}</span>
    </Link>
  )
}

export class FormFooter extends React.PureComponent {
  render() {
    const { cancel, className, submit } = this.props
    const useCancel = Boolean(cancel && cancel.url)
    const useLink = Boolean(submit && submit.url)
    const useSubmit = Boolean(submit && !submit.url)
    const hideSeparator = !useCancel || !submit
    return (
      <footer
        className={`pc-final-form-footer dotted-top-2x-white py7 flex-0 flex-columns text-center items-center fs20 ${className}`}
      >
        {useCancel && renderLinkButton(cancel)}
        {!hideSeparator && <hr className="dotted-left-2x-white flex-0" />}
        {useLink && renderLinkButton(submit)}
        {useSubmit && renderSubmitButton(submit)}
      </footer>
    )
  }
}

FormFooter.defaultProps = {
  cancel: false,
  className: '',
  submit: false,
}

FormFooter.propTypes = {
  cancel: PropTypes.oneOfType([PropTypes.bool, FormFooterObject]),
  className: PropTypes.string,
  submit: PropTypes.oneOfType([PropTypes.bool, FormFooterObject]),
}

export default FormFooter
