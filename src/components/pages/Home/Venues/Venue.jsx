import * as PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

export const Venue = ({ id, isVirtual, name, offererId, publicName }) => (
  <div className="h-section-row nested">
    <div className={`h-card h-card-${isVirtual ? 'primary' : 'secondary'}`}>
      <div className="h-card-inner">
        <div className="h-card-header-row">
          <h3 className="h-card-title">
            <Icon
              className="h-card-title-ico"
              svg={isVirtual ? 'ico-screen-play' : 'ico-box'}
            />
            {publicName || name}
          </h3>
          {!isVirtual && (
            <Link
              className="tertiary-link"
              to={`/structures/${offererId}/lieux/${id}`}
            >
              <Icon svg="ico-outer-pen" />
              {'Modifier'}
            </Link>
          )}
        </div>
      </div>
    </div>
  </div>
)

Venue.defaultProps = {
  id: '',
  isVirtual: false,
  offererId: '',
  publicName: '',
}

Venue.propTypes = {
  id: PropTypes.string,
  isVirtual: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offererId: PropTypes.string,
  publicName: PropTypes.string,
}
