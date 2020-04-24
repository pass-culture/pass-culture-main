import PropTypes from 'prop-types'
import React from 'react'
import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'
import { Criteria } from '../Criteria/Criteria'
import { checkUserIsGeolocated } from '../utils/checkUserIsGeolocated'

export const CriteriaLocation = props => {
  const {
    activeCriterionLabel,
    backTo,
    criteria,
    geolocation,
    history,
    match,
    onCriterionSelection,
    title,
  } = props

  const checkUserCanSelectCriterion = () => {
    return criterionKey => () => {
      checkUserIsGeolocated(criterionKey, geolocation, onCriterionSelection)
    }
  }

  return (
    <div className="criteria-location-page">
      <Header
        backTo={backTo}
        closeTo={null}
        extraClassName="criteria-header"
        history={history}
        location={history.location}
        match={match}
        title={title}
      />
      <div>
        <div className="cl-wrapper">
          <Icon
            className="cl-icon"
            svg="ico-alert"
          />
          <span className="cl-warning-message">
            {`Seules les offres Sorties et Physiques seront affichées pour une recherche avec une localisation`}
          </span>
        </div>
      </div>
      <Criteria
        activeCriterionLabel={activeCriterionLabel}
        backTo={backTo}
        criteria={criteria}
        history={history}
        match={match}
        onCriterionSelection={checkUserCanSelectCriterion()}
        title={title}
      />
    </div>
  )
}
CriteriaLocation.defaultProps = {
  geolocation: {},
}

CriteriaLocation.propTypes = {
  activeCriterionLabel: PropTypes.string.isRequired,
  backTo: PropTypes.string.isRequired,
  criteria: PropTypes.objectOf((propValue, key, componentName, location, propFullName) => {
    if (!propValue[key].label || !propValue[key].icon) {
      return new Error(
        `Invalid prop ${propFullName}. It must contain an 'icon' and a 'label' property.`
      )
    }
  }).isRequired,
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }),
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

export default CriteriaLocation
