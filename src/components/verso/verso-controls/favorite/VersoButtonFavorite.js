import React from 'react'
import PropTypes from 'prop-types'

const DISABLE_FEATURE_NOT_YET_IMPLEMENTED = true

const getButtonIcon = isFavorite => `icon-ico-like${isFavorite ? '-on' : ''}`

const getButtonLabel = isFavorite => (isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris')

const VersoButtonFavorite = ({ isFavorite, onClick, recommendationId }) => (
  <button
    className="no-border no-background"
    disabled={DISABLE_FEATURE_NOT_YET_IMPLEMENTED}
    onClick={onClick(isFavorite, recommendationId)}
    type="button"
  >
    <span
      aria-hidden
      className={getButtonIcon(isFavorite)}
      title={getButtonLabel(isFavorite)}
    />
  </button>
)

VersoButtonFavorite.defaultProps = {
  isFavorite: false,
  recommendationId: null,
}

VersoButtonFavorite.propTypes = {
  isFavorite: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
  recommendationId: PropTypes.string,
}

export default VersoButtonFavorite
