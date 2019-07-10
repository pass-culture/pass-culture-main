import PropTypes from 'prop-types'
import React from 'react'
import { toast } from 'react-toastify'

import { isFeatureDisabled } from '../../../../utils/featureFlipping'

const iconClass = isFavorite => `icon-ico-like${isFavorite ? '-on' : ''}`

const alternativeText = isFavorite => (isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris')

const showFailModal = () => {
  toast('La gestion des favoris ne fonctionne pas pour le moment, veuillez ré-essayer plus tard.')
}

const Favorite = ({ handleFavorite, recommendation }) => {
  const isFavorite = recommendation.offer.favorites.length > 0

  return (
    <button
      className="fav-button"
      disabled={isFeatureDisabled('FAVORITE_OFFER')}
      onClick={handleFavorite(isFavorite, recommendation, showFailModal)}
      type="button"
    >
      <i
        aria-hidden="true"
        className={`font-icon ${iconClass(isFavorite)}`}
        title={alternativeText(isFavorite)}
      />
    </button>
  )
}

Favorite.propTypes = {
  handleFavorite: PropTypes.func.isRequired,
  recommendation: PropTypes.shape().isRequired,
}

export default Favorite
