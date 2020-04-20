import PropTypes from 'prop-types'
import React from 'react'
import findOfferPictoPathByOfferType from './utils/findOfferPictoPathByOfferType'

const VersoHeader = ({ subtitle, title, type }) => {
  return (
    <div className="verso-header with-triangle is-relative pc-theme-black py32 px12">
      {type && (
        <img
          alt=""
          id="verso-offer-type-picto"
          src={findOfferPictoPathByOfferType(type)}
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
  subtitle: null,
  title: null,
  type: null,
}

VersoHeader.propTypes = {
  subtitle: PropTypes.string,
  title: PropTypes.string,
  type: PropTypes.string,
}

export default VersoHeader
