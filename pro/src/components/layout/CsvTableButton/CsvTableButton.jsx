import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class CsvTableButton extends PureComponent {
  handleRedirectToUrl = () => {
    const { history, href, location, url } = this.props
    const { pathname } = location
    const nextUrl = url ? url : pathname + '/detail'
    history.push(nextUrl, href)
  }

  render() {
    const { children, isDisabled } = this.props
    return (
      <button
        className="secondary-button"
        disabled={isDisabled}
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
  isDisabled: false,
  url: undefined,
}

CsvTableButton.propTypes = {
  children: PropTypes.string,
  history: PropTypes.shape().isRequired,
  href: PropTypes.string.isRequired,
  isDisabled: PropTypes.bool,
  location: PropTypes.shape().isRequired,
  url: PropTypes.string,
}

export default CsvTableButton
