/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt standard "Gaël: migration from classes components to function components"
*/

import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class CsvTableButton extends PureComponent {
  handleRedirectToUrl = () => {
    const { history, href, location } = this.props
    const { pathname } = location
    const nextUrl = pathname + '/detail'
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
}

CsvTableButton.propTypes = {
  children: PropTypes.string,
  history: PropTypes.shape().isRequired,
  href: PropTypes.string.isRequired,
  isDisabled: PropTypes.bool,
  location: PropTypes.shape().isRequired,
}

export default CsvTableButton
