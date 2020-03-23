import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import { CriterionItem } from './CriterionItem/CriterionItem'
import { checkIfAroundMe } from '../utils/checkIfAroundMe'

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
    const autourDeMoi = checkIfAroundMe(geolocationCriterion.isSearchAroundMe)
    const categories = categoryCriterion.filters.join(';')
    const tri = sortCriterion.index

    history.push({
      pathname: '/recherche-offres/resultats',
      search: `?mots-cles=${keywordsToSearch}&autour-de-moi=${autourDeMoi}&tri=${tri}&categories=${categories}`,
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
      <main className="search-home-page">
        <div className="sh-header-wrapper">
          <HeaderContainer
            closeTitle="Retourner à la page découverte"
            closeTo="/decouverte"
            extraClassName="home-header"
            title="Recherche"
          />
          <form
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
                type="text"
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
            linkTo="/recherche-offres/criteres-categorie"
            selectedFilter={categoryCriterion.label}
          />
          <span className="sh-criteria-separator" />
          <CriterionItem
            icon={geolocationCriterion.params.icon}
            label="Où"
            linkTo="/recherche-offres/criteres-localisation"
            selectedFilter={geolocationCriterion.params.label}
          />
          <span className="sh-criteria-separator" />
          <CriterionItem
            icon={sortCriterion.icon}
            label="Trier par"
            linkTo="/recherche-offres/criteres-tri"
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
        <RelativeFooterContainer
          extraClassName="dotted-top-red"
          theme="white"
        />
      </main>
    )
  }
}

Home.propTypes = {
  categoryCriterion: PropTypes.shape({
    filters: PropTypes.arrayOf(String),
    icon: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
  }).isRequired,
  geolocationCriterion: PropTypes.shape({
    isSearchAroundMe: PropTypes.bool.isRequired,
    params: PropTypes.shape({
      icon: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      requiresGeolocation: PropTypes.bool.isRequired,
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
