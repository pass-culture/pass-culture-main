import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'
import { Criteria } from '../Criteria/Criteria'
import { checkUserIsGeolocated } from '../utils/checkUserIsGeolocated'
import { Place } from './Place/Place'

class CriteriaLocation extends Component {
  constructor(props) {
    super(props)
    this.state = {
      placeName: null
    }
  }

  checkUserCanSelectCriterion = () => {
    const { geolocation, onCriterionSelection } = this.props
    return criterionKey => () => {
      checkUserIsGeolocated(criterionKey, geolocation, onCriterionSelection)
    }
  }

  redirectToSearchPlacePage = () => {
    const { history } = this.props
    const { location } = history
    const { pathname, search } = location

    history.push(`${pathname}/place${search}`)
  }

  handleUpdatePlaceInformation = (place) => {
    const { name } = place

    this.setState({
      placeName: name
    }, () => {
      const { onPlaceSelection } = this.props
      onPlaceSelection(name)
    })
  }

  render() {
    const {
      activeCriterionLabel,
      backTo,
      criteria,
      history,
      match,
      title,
    } = this.props
    const { location } = history
    const { pathname } = location

    return (
      <div className="criteria-location-page">
        {!pathname.includes('place') ?
          <div>
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
            <div className="cl-place-wrapper">
              <Icon
                className="cl-icon"
                svg="ico-there"
              />
              <button
                onClick={this.redirectToSearchPlacePage}
                type="button">
                {this.state.placeName ? this.state.placeName : 'Choisir un lieu'}
              </button>
            </div>
            <Criteria
              activeCriterionLabel={activeCriterionLabel}
              backTo={backTo}
              criteria={criteria}
              history={history}
              match={match}
              onCriterionSelection={this.checkUserCanSelectCriterion()}
              title={title}
            />
          </div>
          :
          <Place
            backTo={backTo}
            history={history}
            match={match}
            title={'Choisir un lieu'}
            updatePlaceInformation={this.handleUpdatePlaceInformation}
          />
        }
      </div>
    )
  }
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
