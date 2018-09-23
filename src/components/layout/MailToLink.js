import React from 'react'
import PropTypes from 'prop-types'

const toSearchString = (searchParams = {}) =>
  Object.keys(searchParams)
    .map(key => `${key}=${encodeURIComponent(searchParams[key])}`)
    .join('&')

const createMailToLink = (email, headers) => {
  let link = `mailto:${email}`
  if (headers) link = `${link}?${toSearchString(headers)}`
  return link
}

class MailToLink extends React.PureComponent {
  handleClick = event => {
    event.preventDefault()
    const { email, headers } = this.props
    window.location.href = createMailToLink(email, headers)
  }

  renderLink = () => {
    const { email, obfuscate, headers, children, ...others } = this.props
    return (
      <a href={createMailToLink(email, headers)} {...others}>
        {children}
      </a>
    )
  }

  renderObfuscatedLink = () => {
    const { email, obfuscate, headers, children, ...others } = this.props
    return (
      <a onClick={this.handleClick} href="mailto:obfuscated" {...others}>
        {children}
      </a>
    )
  }

  render() {
    const { obfuscate } = this.props
    return obfuscate ? this.renderObfuscatedLink() : this.renderLink()
  }
}

MailToLink.defaultProps = {
  className: '',
  headers: {},
  obfuscate: false,
}

MailToLink.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  email: PropTypes.string.isRequired,
  headers: PropTypes.object,
  obfuscate: PropTypes.bool,
}

export default MailToLink
