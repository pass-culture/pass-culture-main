import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../../../layout/Icon/Icon'

const ErrorPage = ({ refreshPage }) => {
  return (
    <div className="erp-wrapper">
      <Icon
        svg='ico-maintenance'
      />
      <h1>
        {'Oh non !'}
      </h1>
      <div className="erp-text-wrapper">
        <span>
          {'Une erreur s’est produite pendant'}
        </span>
        <span>
          {'le chargement de la page.'}
        </span>
      </div>
      <button
        className="erp-button"
        onClick={refreshPage}
        type="button"
      >
        {'Réessayer'}
      </button>
    </div>
  )
}

export default ErrorPage

ErrorPage.propTypes = {
  refreshPage: PropTypes.func.isRequired,
}
