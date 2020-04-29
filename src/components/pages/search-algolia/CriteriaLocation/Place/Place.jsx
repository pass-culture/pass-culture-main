import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import Header from '../../../../layout/Header/Header'
import { fetchPlaces } from '../../../../../vendor/api-geo/placesService'
import Icon from '../../../../layout/Icon/Icon'

export class Place extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      keywords: '',
      suggestedPlaces: [],
    }
  }

  handleOnChange = event => {
    this.setState({ keywords: event.target.value }, () => {
      const { keywords } = this.state
      fetchPlaces({ keywords })
        .then(suggestedPlaces => {
          this.setState({ suggestedPlaces })
        })
    })
  }

  handlePlaceSelection = event => {
    const { suggestedPlaces } = this.state
    const { history, onPlaceSelection } = this.props
    const { location } = history
    const { pathname, search } = location
    const index = event.currentTarget.value

    const place = suggestedPlaces[index]
    onPlaceSelection(place)

    const pathnameWithoutPlace = pathname.replace('/place', '')
    history.push(`${pathnameWithoutPlace}${search}`)
  }

  handleReset = () => {
    this.setState({
      keywords: '',
    })
  }

  render() {
    const { backTo, history, match, title } = this.props
    const { keywords, suggestedPlaces } = this.state
    return (
      <div className="place-page">
        <Header
          backTo={backTo}
          closeTo={null}
          extraClassName="criteria-header"
          history={history}
          location={history.location}
          match={match}
          title={title}
        />
        <div className="place-wrapper">
          <div className="place-input-wrapper">
            <input
              className="place-text-input"
              name="keywords"
              onChange={this.handleOnChange}
              placeholder="Choisir un lieu..."
              type="search"
              value={keywords}
            />
            <div className="place-reset-wrapper">
              {keywords && (
                <button
                  className="place-reset-button"
                  onClick={this.handleReset}
                  type="reset"
                >
                  <Icon
                    alt="Supprimer la saisie"
                    svg="picto-reset"
                  />
                </button>
              )}
            </div>
          </div>
          {suggestedPlaces.length > 0 && (
            <ul className="place-suggestions">
              {suggestedPlaces.map((suggestedPlace, index) => (
                <li
                  key={`${suggestedPlace.geolocation.latitude}-${suggestedPlace.geolocation.longitude}`}
                >
                  <button
                    onClick={this.handlePlaceSelection}
                    type="button"
                    value={index}
                  >
                    <span className="place-name">
                      {`${suggestedPlace.name} `}
                    </span>
                    <span className="place-extra-data">
                      {`${suggestedPlace.extraData.department}`}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    )
  }
}

Place.propTypes = {
  backTo: PropTypes.string.isRequired,
  history: PropTypes.shape({
    location: PropTypes.shape(),
    replace: PropTypes.func.isRequired,
    push: PropTypes.func.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({}).isRequired,
  }).isRequired,
  onPlaceSelection: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
}
