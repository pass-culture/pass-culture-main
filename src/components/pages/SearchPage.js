import PropTypes from 'prop-types'
import React from 'react'

import { Icon } from 'pass-culture-shared'
import items from './searchPage-results'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import SearchResultItem from '../SearchResultItem'

const renderPageHeader = () => (
  <header>
    <h1>
Recherche
    </h1>
  </header>
)

const renderPageFooter = () => {
  const footerProps = { borderTop: true }
  return <Footer {...footerProps} />
}

const SearchPage = ({ handleSearchChange, search }) => (
  <Main header={renderPageHeader} name="search" footer={renderPageFooter} redBg>
    <div>
      <form className="section" onSubmit={handleSearchChange}>
        <label className="label" htmlFor="search">
          Rechercher une offre :
        </label>
        <div className="field is-grouped">
          <p className="control is-expanded">
            <input
              id="search"
              className="input search-input"
              placeholder="Saisissez une recherche"
              type="text"
              defaultValue={search}
            />
          </p>
          <p className="control">
            <button type="submit" className="button is-primary is-outlined">
              OK
            </button>
            {' '}
            <button type="button" className="button is-secondary">
              &nbsp;
              <Icon svg="ico-filter" />
              &nbsp;
            </button>
          </p>
        </div>
      </form>
    </div>
    <ul className="search-results">
      {items.map(item => (
        <SearchResultItem key={item.id} recommendation={item} />
      ))}
    </ul>
  </Main>
)

SearchPage.propTypes = {
  handleSearchChange: PropTypes.func.isRequired,
  search: PropTypes.object.isRequired,
}

export default SearchPage
