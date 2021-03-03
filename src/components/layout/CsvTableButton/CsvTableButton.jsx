import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

class CsvTableButton extends PureComponent {
  handleRedirectToUrl = () => {
    const { history, href, location } = this.props
    const { pathname } = location
    const nextUrl = pathname + '/detail'
    history.push(nextUrl, href)
  }

  render() {
    const { children } = this.props
    return (
      <button
        className="secondary-button"
        onClick={this.handleRedirectToUrl}
        type="button"
      >
        {children}
      </button>
    )
  }
}

CsvTableButton.defaultProps = {
  children: '',
}

CsvTableButton.propTypes = {
  children: PropTypes.string,
  history: PropTypes.shape().isRequired,
  href: PropTypes.string.isRequired,
  location: PropTypes.shape().isRequired,
}

export default CsvTableButton
