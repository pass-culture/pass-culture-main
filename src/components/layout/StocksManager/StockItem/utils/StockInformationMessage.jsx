import React from 'react'
import PropTypes from 'prop-types'

const ALLOCINE_PROVIDER_NAME = 'Allociné'

const StockInformationMessage = ({ providerName }) => (
  <i>
    {'Il n’est pas possible d’ajouter '}
    {providerName !== ALLOCINE_PROVIDER_NAME ? 'ni de supprimer ' : ''}
    {`d’horaires pour cet événement ${providerName}`}
  </i>
)

StockInformationMessage.propTypes = {
  providerName: PropTypes.string.isRequired,
}

export default StockInformationMessage
