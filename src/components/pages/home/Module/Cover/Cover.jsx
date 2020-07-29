import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../../../../layout/Icon/Icon'
import { PANE_LAYOUT } from '../../domain/layout'

const Cover = ({ img, layout }) => {
  return (
    <li
      className="offer-cover-wrapper"
      key='offer-cover'
    >
      <div className="ofw-image-wrapper">
        <img
          alt=""
          className={layout === PANE_LAYOUT['ONE-ITEM-MEDIUM'] ? "ofw-image-one-item" : "ofw-image-two-items"}
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

Cover.defaultProps = {
  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
}

Cover.propTypes = {
  img: PropTypes.string.isRequired,
  layout: PropTypes.string,
}

export default Cover
