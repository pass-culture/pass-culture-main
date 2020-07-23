import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../../../../layout/Icon/Icon'

const Cover = ({ img }) => {
  return (
    <li
      className="offer-cover-wrapper"
      key='offer-cover'
    >
      <div className="ofw-image-wrapper">
        <img
          alt=""
          className="ofw-image"
          src={img}
        />
        <div className="ofw-swipe-icon-wrapper">
          <Icon
            className="ofw-swipe-icon"
            svg="ico-swipe-tile"
          />
        </div>
      </div>
    </li>
  )
}

Cover.propTypes = {
  img: PropTypes.string.isRequired,
}

export default Cover
