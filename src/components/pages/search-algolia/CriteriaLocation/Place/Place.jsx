import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Header from '../../../../layout/Header/Header'
import { fetchPlaces } from '../../../../../vendor/api-geo/placesService'
import Icon from '../../../../layout/Icon/Icon'
import debounce from 'lodash.debounce'

const WAITING_TIME_BEFORE_FETCHING_DATA_IN_MILLISECONDS = 300

class Place extends Component {
  constructor(props) {
    super(props)
    this.state = {
      keywords: '',
      suggestedPlaces: [],
    }
    this.inputRef = React.createRef()
  }

  componentDidMount() {
    this.inputRef.current.focus()
  }

  shouldComponentUpdate() {
    return true
  }

  handleOnChange = event => {
    const searchedKeywords = event.target.value

    this.setState({ keywords: searchedKeywords })
    this.triggerFetchPlaces(searchedKeywords)
  }

  triggerFetchPlaces = debounce((keywords) => {
    fetchPlaces({ keywords })
      .then(suggestedPlaces => {
        this.setState({ suggestedPlaces })
      })
  }, WAITING_TIME_BEFORE_FETCHING_DATA_IN_MILLISECONDS)

  handlePlaceSelection = event => {
    const { suggestedPlaces } = this.state
    const { history, onPlaceSelection } = this.props
    const { location } = history
    const { pathname, search } = location
    const index = event.currentTarget.value

    const place = suggestedPlaces[index]
    onPlaceSelection(place)

    const pathnameWithoutLocation = pathname
      .replace('/criteres-localisation', '')
      .replace('/localisation', '')
      .replace('/place', '')
    history.push(`${pathnameWithoutLocation}${search}`)
  }

  handleReset = () => {
    this.setState({
      keywords: '',
      suggestedPlaces: []
    })
    this.inputRef.current.focus()
  }

  blurInput = () => () => this.inputRef.current.blur()

  handleOnSubmit = (event) => {
    event.preventDefault()
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
        <div
          className="place-wrapper"
          onScroll={this.blurInput()}
        >
          <div className="place-form-wrapper">
            <form
              action=""
              onSubmit={this.handleOnSubmit}
            >
              <input
                className="place-text-input"
                name="search"
                onChange={this.handleOnChange}
                placeholder="Choisir un lieu..."
                ref={this.inputRef}
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
            </form>
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
                      {suggestedPlace.name}
                    </span>
                    <span className="place-extra-data">
                      {suggestedPlace.extraData.department}
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

Place
  .propTypes = {
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

export default Place
