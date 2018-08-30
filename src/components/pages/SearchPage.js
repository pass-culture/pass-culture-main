import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import { Icon, withSearch } from 'pass-culture-shared'
// import items from './searchPage-results'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import SearchResultItem from '../SearchResultItem'
import { selectRecommendations } from '../../selectors'

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

class SearchPage extends Component {
  handleDataRequest = () => 'data'

  render() {
    const { handleSearchChange, queryParams, recommendations } = this.props

    const { search } = queryParams || {}

    console.log(
      'recommendations recommendations recommendations',
      recommendations[0]
    )

    const items = recommendations

    return (
      <Main
        header={renderPageHeader}
        name="search"
        footer={renderPageFooter}
        redBg
      >
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
            // TODO SearchResultItem based on booking so for events only
          ))}
        </ul>
      </Main>
    )
  }
}

SearchPage.propTypes = {
  handleSearchChange: PropTypes.func.isRequired,
  // search: PropTypes.object.isRequired,
  queryParams: PropTypes.object.isRequired,
  recommendations: PropTypes.array.isRequired,
}

const mapStateToProps = state => {
  const recommendations = selectRecommendations(state)
  return { recommendations }
}

export default compose(
  withSearch({
    dataKey: 'offers',
    defaultQueryParams: {
      search: undefined,
    },
  }),
  connect(mapStateToProps)
)(SearchPage)
