import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'
import { Criteria } from '../Criteria/Criteria'
import { checkUserIsGeolocated } from '../utils/checkUserIsGeolocated'
import { Place } from './Place/Place'

class CriteriaLocation extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      place: props.place
    }
  }

  checkUserCanSelectCriterion = () => {
    const { geolocation, onCriterionSelection } = this.props
    return criterionKey => () => {
      checkUserIsGeolocated(criterionKey, geolocation, onCriterionSelection)
    }
  }

  handleRedirectToPlacePage = () => {
    const { history } = this.props
    const { location } = history
    const { pathname, search } = location

    history.push(`${pathname}/place${search}`)
  }

  handleUpdatePlaceInformation = (place) => {
    this.setState({
      place: place
    }, () => {
      const { history, onPlaceSelection } = this.props
      const { location: { pathname, search } } = history
      onPlaceSelection(place)
      const pathnameWithoutLocation = pathname
        .replace('/criteres-localisation', '')
        .replace('/localisation', '')
      history.push(`${pathnameWithoutLocation}${search}`)
    })
  }

  buildBackToUrl = () => {
    const { history } = this.props
    const { location } = history
    const { pathname, search } = location

    const pathnameWithoutPlace = pathname.replace('/place', '')
    return `${pathnameWithoutPlace}${search}`
  }

  checkIfIsPlacePage = () => {
    const { history } = this.props
    const { location } = history
    const { pathname } = location

    return pathname.includes('place')
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
    const { place } = this.state

    return (
      <div className="criteria-location-page">
        {this.checkIfIsPlacePage() ?
          <Place
            backTo={this.buildBackToUrl()}
            history={history}
            match={match}
            onPlaceSelection={this.handleUpdatePlaceInformation}
            title='Choisir un lieu'
          />
          :
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
                className={place ? 'cl-icon-active' : 'cl-icon'}
                svg="ico-there"
              />
              <button
                className={place ? 'cl-place-button-active' : 'cl-place-button'}
                onClick={this.handleRedirectToPlacePage}
                type="button"
              >
                {place ? place.name : 'Choisir un lieu'}
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
          </div>}
      </div>
    )
  }
}

CriteriaLocation.defaultProps = {
  geolocation: {},
  place: {
    geolocation: { latitude: null, longitude: null },
    name: null
  },
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
  onPlaceSelection: PropTypes.func.isRequired,
  place: PropTypes.shape({
    geolocation: PropTypes.shape({
      latitude: PropTypes.number,
      longitude: PropTypes.number,
    }),
    name: PropTypes.string
  }),
  title: PropTypes.string.isRequired,
}

export default CriteriaLocation
