import React from 'react'
import PropTypes from 'prop-types'

import createMailToLink from './utils'

class MailToLink extends React.PureComponent {
  handleClick = event => {
    event.preventDefault()
    const { email, headers } = this.props
    // NOTE -> il doit y avoir un peu mieux, par exemple passer par l'API HTML5
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
  email: null,
  headers: {},
  obfuscate: false,
}

MailToLink.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  email: PropTypes.string,
  headers: PropTypes.object,
  obfuscate: PropTypes.bool,
}

export default MailToLink
