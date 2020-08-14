import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import PrimaryButton from "../buttons/PrimaryButton/PrimaryButton"

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
      <PrimaryButton
        onClick={this.handleRedirectToUrl}
        text={children}
      />
    )
  }
}

CsvTableButton.defaultProps = {
  children: ''
}

CsvTableButton.propTypes = {
  children: PropTypes.string,
  href: PropTypes.string.isRequired,
}

export default CsvTableButton
