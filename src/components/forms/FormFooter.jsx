import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Link } from 'react-router-dom'

import { FormFooterObject } from '../../types'

export class FormFooter extends Component {
  renderSubmitButton = obj => {
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

  renderLinkButton = obj => {
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

  renderExternalLinkButton = obj => {
    const props = {
      className: `flex-1 ${obj.className || ''}`,
      disabled: obj.disabled,
      href: obj.url,
      target: obj.target,
    }
    if (obj.id) props.id = obj.id
    return (
      <a {...props}>
        <span className="is-block">{obj.label}</span>
      </a>
    )
  }

  render() {
    const { cancel, className, externalLink, submit } = this.props
    const useCancel = Boolean(cancel && cancel.url)
    const useExternalLink = Boolean(externalLink && externalLink.url)
    const useLink = Boolean(submit && submit.url)
    const useSubmit = Boolean(submit && !submit.url)
    const hideSeparator = !(useCancel || useExternalLink) || !submit

    return (
      <footer
        className={`pc-final-form-footer dotted-top-2x-white py7 flex-0 flex-columns text-center items-center fs20 ${className}`}
      >
        {useCancel && this.renderLinkButton(cancel)}
        {useExternalLink && this.renderExternalLinkButton(externalLink)}
        {!hideSeparator && <hr className="dotted-left-2x-white flex-0" />}
        {useLink && this.renderLinkButton(submit)}
        {useSubmit && this.renderSubmitButton(submit)}
      </footer>
    )
  }
}

FormFooter.defaultProps = {
  cancel: false,
  className: '',
  externalLink: false,
  submit: false,
}

FormFooter.propTypes = {
  cancel: PropTypes.oneOfType([PropTypes.bool, FormFooterObject]),
  className: PropTypes.string,
  externalLink: PropTypes.oneOfType([PropTypes.bool, FormFooterObject]),
  submit: PropTypes.oneOfType([PropTypes.bool, FormFooterObject]),
}

export default FormFooter
