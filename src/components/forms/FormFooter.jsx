import { arrayOf, bool, shape, string } from 'prop-types'
import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'

class FormFooter extends PureComponent {
  isDisplayedOnInstagram() {
    const userAgent = navigator.userAgent
    return userAgent.includes('Instagram') && userAgent.includes('iPhone')
  }

  renderSubmitButton = options => {
    const attributes = {
      className: `flex-1 ${options.className || ''}`,
      disabled: options.disabled,
      id: options.id,
      key: options.id,
    }
    return (
      <button
        type="submit"
        {...attributes}
      >
        {options.label}
      </button>
    )
  }

  renderLink = options => {
    const attributes = {
      className: `flex-1 ${options.className || ''}`,
      disabled: options.disabled,
      id: options.id,
      key: options.id,
      to: options.url,
    }
    return (
      <Link
        {...attributes}
        onClick={this.handleTracking(options)}
        onKeyPress={this.handleTracking(options)}
      >
        {options.label}
      </Link>
    )
  }

  handleTracking = options => () => {
    if (options.tracker) {
      options.tracker()
    }
  }

  renderInnerLinkOrSubmitButton = (innerLinkOrSubmitButton, index, linksOrButtons) => {
    const numberOfLinksOrButton = linksOrButtons.length
    const showSeparator = index + 1 !== numberOfLinksOrButton
    const isInnerLink = innerLinkOrSubmitButton.url
    return [
      isInnerLink
        ? this.renderLink(innerLinkOrSubmitButton)
        : this.renderSubmitButton(innerLinkOrSubmitButton),
      showSeparator && this.renderSeparator(),
    ]
  }

  renderSeparator = () => <hr className="dotted-left-2x-white flex-0" />

  render() {
    const { cancel, submit } = this.props
    const isCancelLink = Boolean(cancel && cancel.url)
    const showSeparator = isCancelLink && submit

    if (this.isDisplayedOnInstagram()) {
      const arbitraryValueToScrollToTheBottom = 10000
      window.scrollTo(0, arbitraryValueToScrollToTheBottom)
    }

    return (
      <footer
        className={`logout-form-footer ${
          this.isDisplayedOnInstagram() ? 'logout-form-footer-instagram' : ''
        }`}
        id="logout-form-footer"
      >
        {isCancelLink && this.renderLink(cancel)}
        {showSeparator && this.renderSeparator()}
        {submit && submit.map(this.renderInnerLinkOrSubmitButton)}
      </footer>
    )
  }
}

FormFooter.defaultProps = {
  cancel: null,
  submit: null,
}

FormFooter.propTypes = {
  cancel: shape({
    className: string,
    disabled: bool,
    id: string,
    label: string.isRequired,
    url: string,
  }),
  submit: arrayOf(
    shape({
      className: string,
      disabled: bool,
      id: string,
      label: string.isRequired,
      url: string,
    })
  ),
}

export default FormFooter
