import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Link } from 'react-router-dom'

import { FormFooterObject } from '../../types'

class FormFooter extends Component {
  renderSubmitButton = buttonOptions => {
    const attributes = {
      className: `flex-1 ${buttonOptions.className || ''}`,
      disabled: buttonOptions.disabled,
      id: buttonOptions.id,
    }
    return (
      <button
        type="submit"
        {...attributes}
      >
        {buttonOptions.label}
      </button>
    )
  }

  renderLink = linkOptions => {
    const attributes = {
      className: `flex-1 ${linkOptions.className || ''}`,
      disabled: linkOptions.disabled,
      id: linkOptions.id,
      to: linkOptions.url,
    }
    return <Link {...attributes}>{linkOptions.label}</Link>
  }

  renderExternalLink = linkOptions => {
    const attributes = {
      className: `flex-1 ${linkOptions.className || ''}`,
      href: linkOptions.url,
      id: linkOptions.id,
      target: linkOptions.target,
    }
    return <a {...attributes}>{linkOptions.label}</a>
  }

  render() {
    const { cancel, className, externalLink, submit } = this.props
    const useCancel = Boolean(cancel && cancel.url)
    const useExternalLink = Boolean(externalLink && externalLink.url)
    const useLink = Boolean(submit && submit.url)
    const useSubmit = Boolean(submit && !submit.url)
    const hideSeparator = !(useCancel || useExternalLink) || !submit

    return (
      <footer className={`logout-form-footer ${className}`}>
        {useCancel && this.renderLink(cancel)}
        {useExternalLink && this.renderExternalLink(externalLink)}
        {!hideSeparator && <hr className="dotted-left-2x-white flex-0" />}
        {useLink && this.renderLink(submit)}
        {useSubmit && this.renderSubmitButton(submit)}
      </footer>
    )
  }
}

FormFooter.defaultProps = {
  cancel: null,
  className: '',
  externalLink: null,
  submit: null,
}

FormFooter.propTypes = {
  cancel: FormFooterObject,
  className: PropTypes.string,
  externalLink: PropTypes.shape({
    className: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string.isRequired,
    url: PropTypes.string,
  }),
  submit: FormFooterObject,
}

export default FormFooter
