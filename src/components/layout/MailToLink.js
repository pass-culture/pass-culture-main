import React from 'react'
import PropTypes from 'prop-types'

import createMailToLink from '../../helpers/createMailToLink'

class MailToLink extends React.PureComponent {
  handleObfuscatedClick = event => {
    event.preventDefault()
    const { email, headers } = this.props
    // NOTE -> il doit y avoir un peu mieux, par exemple passer par l'API HTML5
    window.location.href = createMailToLink(email, headers)
  }

  renderLink = () => {
    const { email, headers, children, ...others } = this.props
    return (
      <a
        href={createMailToLink(email, headers)}
        {...others}
      >
        {children}
      </a>
    )
  }

  renderObfuscatedLink = () => {
    const { children, ...others } = this.props
    return (
      <a
        href="mailto:obfuscated"
        onClick={this.handleObfuscatedClick}
        {...others}
      >
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
  headers: PropTypes.shape(),
  obfuscate: PropTypes.bool,
}

export default MailToLink
