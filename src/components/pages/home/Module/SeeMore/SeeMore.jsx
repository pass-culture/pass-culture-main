import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../../../../layout/Icon/Icon'
import { PANE_LAYOUT } from '../../domain/layout'

const SeeMore = ({ layout, parameters }) => {
  return (
    <li
      className="see-more-wrapper"
      key='see-more'
    >
      <div className="smw-image-one-item-medium">
        <div className="smw-content-wrapper">
          <Icon
            className="smw-icon-wrapper"
            svg="ico-offres-home"
          />
          <span>
            {'En voir plus'}
          </span>
        </div>
      </div>
    </li>
  )
}

SeeMore.defaultProps = {
  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
}

SeeMore.propTypes = {
  layout: PropTypes.string,
  parameters: PropTypes.shape().isRequired,
}

export default SeeMore
