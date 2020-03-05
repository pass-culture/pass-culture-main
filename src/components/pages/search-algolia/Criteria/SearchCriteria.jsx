import PropTypes from 'prop-types'
import React from 'react'
import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'

export const SearchCriteria = props => {
  const {
    location,
    match,
    history,
    activeCriterionLabel,
    onCriterionSelection,
    title,
    criteria,
  } = props

  return (
    <div>
      <Header
        backTo="/recherche-offres"
        closeTo=""
        extraClassName="sc-header"
        history={history}
        location={location}
        match={match}
        title={title}
      />
      <ul className="sc-item-list">
        {Object.keys(criteria).map(criterionKey => {
          const label = criteria[criterionKey].label
          const icon = criteria[criterionKey].icon
          const isActive = activeCriterionLabel === label
          return (
            <li key={label}>
              <button
                className="sc-item"
                onClick={onCriterionSelection(criterionKey)}
                type="button"
              >
                <div className={`sc-item-icon-bg ${isActive && 'sc-active-icon'}`}>
                  <Icon
                    className="sc-item-icon"
                    svg={icon}
                  />
                </div>
                <span className={`sc-item-label ${isActive && 'sc-active-label'}`}>
                  {label}
                </span>
                {isActive && <Icon
                  className="sc-item-icon-check"
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

SearchCriteria.propTypes = {
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
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  onCriterionSelection: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
}
