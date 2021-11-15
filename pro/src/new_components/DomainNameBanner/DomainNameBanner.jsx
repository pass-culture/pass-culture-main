import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'

export const DomainNameBanner = ({ handleOnClick }) => {
  const isOnVenuePage = window.location.href.indexOf('lieux') > -1
  return (
    <Banner
      className={isOnVenuePage ? 'venue-domain-name-banner' : ''}
      closable
      handleOnClick={handleOnClick}
      linkTitle={"Consulter les Conditions Générales d'Utilisation"}
      type="attention"
    >
      Notre nom de domaine évolue ! Vous avez été automatiquement redirigé
      vers&nbsp;
      <strong>https://passculture.pro</strong>
    </Banner>
  )
}

DomainNameBanner.propTypes = {
  handleOnClick: PropTypes.func.isRequired,
}
