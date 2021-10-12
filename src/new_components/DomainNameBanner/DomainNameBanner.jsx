import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'

export const DomainNameBanner = ({ handleOnClick }) => {
  return (
    <Banner
      closable
      handleOnClick={handleOnClick}
      linkTitle={"Consulter les Conditions Générales d'Utilisation"}
      type="attention"
    >
      Notre nom de domaine évolue ! Vous avez été automatiquement redirigé vers&nbsp;
      <strong>
        https://passculture.pro
      </strong>
      <br />
      La redirection automatique cessera au 15/01/2022.
    </Banner>
  )
}

DomainNameBanner.propTypes = {
  handleOnClick: PropTypes.func.isRequired,
}
