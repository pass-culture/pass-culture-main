import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'
import { CATEGORY_CRITERIA } from './searchCriteriaValues'

class CategoryCriteria extends PureComponent {
  handleCriterionSelection = criterionKey => () => {
    const { onCriterionSelection } = this.props
    onCriterionSelection(criterionKey)
  }

  render() {
    const { location, match, history, activeCriterionLabel } = this.props
    return (
      <div>
        <Header
          backTo="/recherche-offres"
          closeTo=""
          extraClassName="gc-header"
          history={history}
          location={location}
          match={match}
          title="Catégories"
        />
        <ul className="gc-item-list">
          {Object.keys(CATEGORY_CRITERIA).map(criterionKey => {
            const label = CATEGORY_CRITERIA[criterionKey].label
            const icon = CATEGORY_CRITERIA[criterionKey].icon
            const isActive = activeCriterionLabel === label
            return (
              <li key={label}>
                <button
                  className="gc-item"
                  onClick={this.handleCriterionSelection(criterionKey)}
                  type="button"
                >
                  <div className={`gc-item-icon-bg ${isActive && 'gc-active-icon'}`}>
                    <Icon
                      className="gc-item-icon"
                      svg={icon}
                    />
                  </div>
                  <span className={`gc-item-label ${isActive && 'gc-active-label'}`}>
                    {label}
                  </span>
                  {isActive && <Icon
                    className="gc-item-icon-check"
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
}

CategoryCriteria.propTypes = {
  activeCriterionLabel: PropTypes.string.isRequired,
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
}

export default CategoryCriteria
