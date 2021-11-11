import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'
import Icon from '../../../../layout/Icon/Icon'

export const CriterionItem = ({ icon, label, selectedFilter, linkTo }) => (
  <li className="ci-wrapper">
    <div className="ci-link-label">
      <span>
        {label}
      </span>
    </div>
    <Link
      className="ci-page-link"
      to={linkTo}
    >
      <Icon
        className="ci-page-icon"
        svg={icon}
      />
      <span>
        {selectedFilter}
      </span>
    </Link>
  </li>
)

CriterionItem.propTypes = {
  icon: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  linkTo: PropTypes.string.isRequired,
  selectedFilter: PropTypes.string.isRequired,
}
