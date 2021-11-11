import PropTypes from 'prop-types'
import React from 'react'
import findOfferPictoPathByOfferType from './utils/findOfferPictoPathByOfferType'

const VersoHeader = ({ subtitle, title, subcategory }) => {
  return (
    <div className="verso-header with-triangle is-relative pc-theme-black py32 px12">
      {subcategory && (
        <img
          alt=""
          id="verso-offer-type-picto"
          src={findOfferPictoPathByOfferType(subcategory)}
        />
      )}
      {title && (
        <h1
          className="fs40 is-medium is-hyphens"
          id="verso-offer-name"
        >
          {title}
        </h1>
      )}
      {subtitle && (
        <h2
          className="fs22 is-normal is-hyphens"
          id="verso-offer-venue"
        >
          {subtitle}
        </h2>
      )}
    </div>
  )
}

VersoHeader.defaultProps = {
  subcategory: null,
  subtitle: null,
  title: null,
}

VersoHeader.propTypes = {
  subcategory: PropTypes.shape(),
  subtitle: PropTypes.string,
  title: PropTypes.string,
}

export default VersoHeader
