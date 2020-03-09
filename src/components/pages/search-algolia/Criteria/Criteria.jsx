import PropTypes from 'prop-types'
import React from 'react'
import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'

export const Criteria = props => {
  const { match, history, activeCriterionLabel, onCriterionSelection, title, criteria } = props

  return (
    <div className="criteria-page">
      <Header
        backTo="/recherche-offres"
        closeTo=""
        extraClassName="criteria-header"
        history={history}
        location={history.location}
        match={match}
        title={title}
      />
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
                <div className={`criteria-item-icon-bg ${isActive && 'criteria-active-icon'}`}>
                  <Icon
                    className="criteria-item-icon"
                    svg={icon}
                  />
                </div>
                <span className={`criteria-item-label ${isActive && 'criteria-active-label'}`}>
                  {label}
                </span>
                {isActive && <Icon
                  className="criteria-item-icon-check"
                  svg="ico-check-pink"
                             />}
              </button>
            </li>
          )
        })}
      </ul>
    </div>
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
  history: PropTypes.shape({
    replace: PropTypes.func.isRequired,
    push: PropTypes.func.isRequired,
    location: PropTypes.shape(),
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  onCriterionSelection: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
}
