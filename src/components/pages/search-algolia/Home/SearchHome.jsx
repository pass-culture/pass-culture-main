import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import { SearchFilterListItem } from '../Filters/SearchFilterListItem'

export class SearchHome extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      keywordsToSearch: '',
    }
    this.inputRef = React.createRef()
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { history } = this.props
    const { keywordsToSearch } = this.state
    if (keywordsToSearch) {
      history.push(`/recherche-offres/resultats?mots-cles=${keywordsToSearch}`)
    }
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
    const { geolocationCriterion, categoryCriterion } = this.props
    return (
      <main className="search-page-algolia">
        <div className="sp-header-wrapper">
          <HeaderContainer
            closeTitle="Retourner à la page découverte"
            closeTo="/decouverte"
            extraClassName="header-search-main-page"
            title="Recherche"
          />
          <form
            className="sp-text-input-form"
            onSubmit={this.handleOnSubmit}
          >
            <div className="sp-text-input-wrapper">
              <div className="sp-text-input-back">
                <Icon svg="picto-search" />
              </div>
              <input
                className="sp-text-input"
                name="keywords"
                onChange={this.handleOnTextInputChange}
                placeholder="Artiste, auteur..."
                ref={this.inputRef}
                type="text"
                value={keywordsToSearch}
              />
              <div className="sp-text-input-reset">
                {keywordsToSearch && (
                  <button
                    className="sp-text-input-reset-button"
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
            <div className="sp-search-button-wrapper">
              <button
                className="sp-search-button"
                type="submit"
              >
                {'Rechercher'}
              </button>
            </div>
          </form>
        </div>

        <ul className="sp-filter-list">
          <SearchFilterListItem
            icon={categoryCriterion.icon}
            label="Je cherche"
            linkTo="/recherche-offres/criteres-categorie"
            selectedFilter={categoryCriterion.label}
          />
          <SearchFilterListItem
            icon={geolocationCriterion.params.icon}
            label="Où"
            linkTo="/recherche-offres/criteres-localisation"
            selectedFilter={geolocationCriterion.params.label}
          />
        </ul>

        <RelativeFooterContainer
          extraClassName="dotted-top-red"
          theme="white"
        />
      </main>
    )
  }
}

SearchHome.propTypes = {
  categoryCriterion: PropTypes.shape({
    label: PropTypes.string.isRequired,
    icon: PropTypes.string.isRequired,
  }).isRequired,
  geolocationCriterion: PropTypes.shape({
    params: PropTypes.shape({
      label: PropTypes.string.isRequired,
      icon: PropTypes.string.isRequired,
    }),
  }).isRequired,
  history: PropTypes.shape({ push: PropTypes.func }).isRequired,
}
