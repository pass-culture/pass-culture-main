import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import Header from '../../../../layout/Header/Header'
import { fetchPlaces } from '../../../../../vendor/api-geo/placesService'

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
    const { backTo, history, updatePlaceInformations } = this.props
    const index = event.target.value

    const place = suggestedPlaces[index]
    updatePlaceInformations(place)
    history.push(backTo)
  }

  render() {
    const { backTo, history, match, title } = this.props
    const { keywords, suggestedPlaces } = this.state
    return (
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
        <input
          onChange={this.handleOnChange}
          type="search"
          value={keywords}
        />
        {suggestedPlaces.length > 0 && (
          <ul>
            {suggestedPlaces.map((suggestedPlace, index) => (
              <li
                key={`${suggestedPlace.geolocation.latitude}-${suggestedPlace.geolocation.longitude}`}
              >
                <button
                  onClick={this.handlePlaceSelection}
                  type="button"
                  value={index}
                >
                  {`${suggestedPlace.name} ${suggestedPlace.extraData}`}
                </button>
              </li>
            ))}
          </ul>
        )}
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
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  title: PropTypes.string.isRequired,
  updatePlaceInformations: PropTypes.func.isRequired,
}
