import PropTypes from 'prop-types'
import React from 'react'
import { toast } from 'react-toastify'

const iconClass = isFavorite => `icon-ico-like${isFavorite ? '-on' : ''}`

const alternativeText = isFavorite => (isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris')

const showFailModal = () => {
  toast('La gestion des favoris ne fonctionne pas pour le moment, veuillez ré-essayer plus tard.')
}

const Favorite = ({ handleFavorite, isFavorite, isFeatureDisabled, mediationId, offerId }) => (
  <button
    className="fav-button"
    disabled={isFeatureDisabled}
    onClick={handleFavorite(offerId, mediationId, isFavorite, showFailModal)}
    type="button"
  >
    <i
      aria-hidden="true"
      className={`font-icon ${iconClass(isFavorite)}`}
      title={alternativeText(isFavorite)}
    />
  </button>
)

Favorite.defaultProps = {
  mediationId: null,
}

Favorite.propTypes = {
  handleFavorite: PropTypes.func.isRequired,
  isFavorite: PropTypes.bool.isRequired,
  isFeatureDisabled: PropTypes.bool.isRequired,
  mediationId: PropTypes.string,
  offerId: PropTypes.string.isRequired,
}

export default Favorite
