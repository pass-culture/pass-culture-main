import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../../../layout/Icon/Icon'

export const Criteria = props => {
  const { activeCriterionLabel, criteria, onCriterionSelection } = props

  return (
    <ul className="criteria-item-list">
      {Object.keys(criteria).map(criterionKey => {
        const label = criteria[criterionKey].label
        const icon = criteria[criterionKey].icon
        const isActive = activeCriterionLabel === label
        return (
          <li key={label}>
            <button
              className="criteria-item"
              onClick={onCriterionSelection(criterionKey)}
              type="button"
            >
              <div className="criteria-item-icon-wrapper">
                <Icon
                  className={`${isActive ? 'criteria-item-icon-active' : 'criteria-item-icon'}`}
                  svg={icon}
                />
              </div>
              <span className={`criteria-item-label ${isActive && 'criteria-active-label'}`}>
                {label}
              </span>
              {isActive && (
                <Icon
                  className="criteria-item-icon-check"
                  svg="ico-check-pink"
                />
              )}
            </button>
          </li>
        )
      })}
    </ul>
  )
}

Criteria.propTypes = {
  activeCriterionLabel: PropTypes.string.isRequired,
  criteria: PropTypes.objectOf((propValue, key, componentName, location, propFullName) => {
    if (!propValue[key].label || !propValue[key].icon) {
      return new Error(
        `Invalid prop ${propFullName}. It must contain an 'icon' and a 'label' property.`
      )
    }
  }).isRequired,
  onCriterionSelection: PropTypes.func.isRequired,
}
