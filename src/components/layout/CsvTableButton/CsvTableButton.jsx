import PropTypes from 'prop-types'
import React, { Component } from 'react'

class CsvTableButton extends Component {
  redirectToUrl = () => {
    const { history, href, location } = this.props
    const { pathname } = location
    const nextUrl = pathname + '/detail'
    history.push(nextUrl, href)
  }

  render() {
    const { children } = this.props
    return (
      <button
        className="button is-primary is-flex-button"
        onClick={this.redirectToUrl}
      >
        {children}
      </button>
    )
  }
}

CsvTableButton.propTypes = {
  children: PropTypes.string,
  href: PropTypes.string.isRequired,
}

export default CsvTableButton
