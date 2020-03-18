import Icon from '../../layout/Icon'
import React from 'react'
import PropTypes from 'prop-types'

const OfferPreviewLink = ({ className, offerWebappUrl, onClick }) => {
  return (
    <a
      className={className}
      href={offerWebappUrl}
      onClick={onClick}
      rel="noopener noreferrer"
      target="_blank"
    >
      <span
        data-place="bottom"
        data-tip="<p>Ouvrir un nouvel onglet avec la prévisualisation de l'offre</p>"
        data-type="info"
      >
        <Icon svg="ico-eye" />
      </span>
      {'Prévisualiser'}
    </a>
  )
}

OfferPreviewLink.propTypes = {
  className: PropTypes.string.isRequired,
  offerWebappUrl: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default OfferPreviewLink
