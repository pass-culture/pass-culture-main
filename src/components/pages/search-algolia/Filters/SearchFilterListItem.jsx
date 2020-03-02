import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'
import Icon from '../../../layout/Icon/Icon'

export const SearchFilterListItem = ({ icon, label, selectedFilter, linkTo }) => (
  <li className="sfi-wrapper">
    <div className="sfi-link-label">
      <span>
        {label}
      </span>
    </div>
    <Link
      className="sfi-page-link"
      to={linkTo}
    >
      <Icon
        className="sfi-page-icon"
        svg={icon}
      />
      <span>
        {selectedFilter}
      </span>
    </Link>
  </li>
)

SearchFilterListItem.propTypes = {
  icon: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  linkTo: PropTypes.string.isRequired,
  selectedFilter: PropTypes.string.isRequired,
}
