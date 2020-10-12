import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../Icon'

const OfferPreviewLink = ({ offerWebappUrl, onClick }) => (
  <a
    className="link"
    href={offerWebappUrl}
    onClick={onClick}
    rel="noopener noreferrer"
    target="_blank"
  >
    <span
      data-place="bottom"
      data-tip="Ouvrir un nouvel onglet avec la prévisualisation de l’offre."
      data-type="info"
    >
      <Icon svg="ico-eye" />
    </span>
    {'Prévisualiser'}
  </a>
)

OfferPreviewLink.propTypes = {
  offerWebappUrl: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default OfferPreviewLink
