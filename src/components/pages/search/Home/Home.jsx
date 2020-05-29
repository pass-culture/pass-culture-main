import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import { CriterionItem } from './CriterionItem/CriterionItem'
import { checkIfSearchAround } from '../utils/checkIfSearchAround'

export class Home extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      keywordsToSearch: '',
    }
    this.inputRef = React.createRef()
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { categoryCriterion, geolocationCriterion, history, sortCriterion } = this.props
    const { keywordsToSearch } = this.state
    const { place, searchAround, userGeolocation } = geolocationCriterion
    const { geolocation: placeGeolocation, name } = place || {}
    const { long = '' } = name || {}

    const autourDe = checkIfSearchAround(searchAround)
    const categories = categoryCriterion.facetFilter
    const tri = sortCriterion.index

    const search =
      `?mots-cles=${keywordsToSearch}` +
      `&autour-de=${autourDe}&tri=${tri}&categories=${categories}` +
      `&latitude=${searchAround.place ? placeGeolocation.latitude : userGeolocation.latitude}` +
      `&longitude=${searchAround.place ? placeGeolocation.longitude : userGeolocation.longitude}` +
      `${searchAround.place ? `&place=${long}` : ''}`

    history.push({
      pathname: '/recherche/resultats',
      search,
    })
  }

  handleResetButtonClick = () => {
    this.setState({
      keywordsToSearch: '',
    })
    this.inputRef.current.focus()
  }

  handleOnTextInputChange = event => {
    this.setState({
      keywordsToSearch: event.target.value,
    })
  }

  render() {
    const { keywordsToSearch } = this.state
    const { categoryCriterion, geolocationCriterion, sortCriterion } = this.props
    return (
      <main className="page search-home-page">
        <div className="sh-header-wrapper">
          <HeaderContainer
            closeTitle="Retourner à la page découverte"
            closeTo="/decouverte"
            extraClassName="home-header"
            title="Recherche"
          />
          <form
            action=""
            className="sh-form"
            id="home-form"
            onSubmit={this.handleOnSubmit}
          >
            <div className="sh-input-wrapper">
              <div className="sh-input-back">
                <Icon svg="picto-search" />
              </div>
              <input
                className="sh-text-input"
                name="keywords"
                onChange={this.handleOnTextInputChange}
                placeholder="Titre, artiste..."
                ref={this.inputRef}
                type="search"
                value={keywordsToSearch}
              />
              <div className="sh-reset-wrapper">
                {keywordsToSearch && (
                  <button
                    className="sh-reset-button"
                    onClick={this.handleResetButtonClick}
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
          </form>
        </div>
        <ul className="sh-criteria-list">
          <CriterionItem
            icon={categoryCriterion.icon}
            label="Je cherche"
            linkTo="/recherche/criteres-categorie"
            selectedFilter={categoryCriterion.label}
          />
          <span className="sh-criteria-separator" />
          <CriterionItem
            icon={geolocationCriterion.params.icon}
            label="Où"
            linkTo="/recherche/criteres-localisation"
            selectedFilter={geolocationCriterion.params.label}
          />
          <span className="sh-criteria-separator" />
          <CriterionItem
            icon={sortCriterion.icon}
            label="Trier par"
            linkTo="/recherche/criteres-tri"
            selectedFilter={sortCriterion.label}
          />
        </ul>
        <div className="sh-search-wrapper">
          <button
            className="sh-search-button"
            form="home-form"
            type="submit"
          >
            {'Rechercher'}
          </button>
        </div>
      </main>
    )
  }
}

Home.propTypes = {
  categoryCriterion: PropTypes.shape({
    facetFilter: PropTypes.string.isRequired,
    filters: PropTypes.arrayOf(String),
    icon: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
  }).isRequired,
  geolocationCriterion: PropTypes.shape({
    params: PropTypes.shape({
      icon: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      requiresGeolocation: PropTypes.bool.isRequired,
    }),
    place: PropTypes.shape({
      geolocation: PropTypes.shape({
        latitude: PropTypes.number,
        longitude: PropTypes.number,
      }),
      name: PropTypes.shape({
        long: PropTypes.string,
        short: PropTypes.string,
      }),
    }),
    searchAround: PropTypes.shape({
      everywhere: PropTypes.bool,
      place: PropTypes.bool,
      user: PropTypes.bool,
    }).isRequired,
    userGeolocation: PropTypes.shape({
      latitude: PropTypes.number,
      longitude: PropTypes.number,
    }),
  }).isRequired,
  history: PropTypes.shape({ push: PropTypes.func }).isRequired,
  sortCriterion: PropTypes.shape({
    icon: PropTypes.string.isRequired,
    index: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    requiresGeolocation: PropTypes.bool.isRequired,
  }).isRequired,
}
