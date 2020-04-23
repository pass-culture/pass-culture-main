import PropTypes from 'prop-types'
import React from 'react'
import Header from '../../../layout/Header/Header'
import { Criteria } from '../Criteria/Criteria'

export const CriteriaSort = props => {
  const { activeCriterionLabel, backTo, criteria, history, match, onCriterionSelection, title } = props

  return (
    <div className="criteria-page">
      <Header
        backTo={backTo}
        closeTo={null}
        extraClassName="criteria-header"
        history={history}
        location={history.location}
        match={match}
        title={title}
      />
      <Criteria
        activeCriterionLabel={activeCriterionLabel}
        backTo={backTo}
        criteria={criteria}
        history={history}
        match={match}
        onCriterionSelection={onCriterionSelection}
        title={title}
      />
    </div>
  )
}

CriteriaSort.propTypes = {
  activeCriterionLabel: PropTypes.string.isRequired,
  backTo: PropTypes.string.isRequired,
  criteria: PropTypes.objectOf((propValue, key, componentName, location, propFullName) => {
    if (!propValue[key].label || !propValue[key].icon) {
      return new Error(
        `Invalid prop ${propFullName}. It must contain an 'icon' and a 'label' property.`
      )
    }
  }).isRequired,
  history: PropTypes.shape({
    location: PropTypes.shape(),
    replace: PropTypes.func.isRequired,
    push: PropTypes.func.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  onCriterionSelection: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
}

export default CriteriaSort
