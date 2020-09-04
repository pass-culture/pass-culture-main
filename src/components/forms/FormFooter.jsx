import { arrayOf, bool, shape, string } from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
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

  renderLink = (options, index, links) => {
    const showSeparator = index + 1 !== links.length
    const attributes = {
      className: `flex-1 ${options.className || ''}`,
      disabled: options.disabled,
      id: options.id,
      key: options.id,
      to: options.url,
    }
    return (
      <Fragment key={attributes.id}>
        <Link
          {...attributes}
          onClick={this.handleTracking(options)}
          onKeyPress={this.handleTracking(options)}
        >
          {options.label}
        </Link>
        {showSeparator && this.renderSeparator()}
      </Fragment>
    )
  }

  handleTracking = options => () => {
    if (options.tracker) {
      options.tracker()
    }
  }

  renderSeparator = () => <hr className="dotted-left-2x-white flex-0" />

  render() {
    const { internalLinks, submitButton } = this.props
    const showSeparator = internalLinks.length > 0 && submitButton

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
        {internalLinks.map(this.renderLink)}
        {showSeparator && this.renderSeparator()}
        {submitButton && this.renderSubmitButton(submitButton)}
      </footer>
    )
  }
}

FormFooter.defaultProps = {
  internalLinks: [],
  submitButton: null,
}

FormFooter.propTypes = {
  internalLinks: arrayOf(
    shape({
      className: string,
      disabled: bool,
      id: string,
      label: string.isRequired,
      url: string.isRequired,
    })
  ),
  submitButton: shape({
    className: string,
    disabled: bool,
    id: string,
    label: string.isRequired,
  }),
}

export default FormFooter
