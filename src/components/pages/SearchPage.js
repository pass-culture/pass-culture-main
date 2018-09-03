/* eslint-disabler */

import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import {
  assignData,
  Icon,
  InfiniteScroller,
  Logger,
  requestData,
  showModal,
  withSearch,
} from 'pass-culture-shared'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import SearchResultItem from '../SearchResultItem'
import { selectRecommendations } from '../../selectors'
import searchSelector from '../../selectors/search'

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
  componentDidMount() {
    Logger.log('DiscoveryPage ---> componentDidMount')
  }

  componentWillUnmount() {
    Logger.log('DiscoveryPage ---> componentWillUnmount')
  }

  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { goToNextSearchPage, querySearch, requestData } = this.props // eslint-disable-line no-shadow
    requestData('GET', `recommendations?${querySearch}`, {
      handleFail,
      handleSuccess: (state, action) => {
        handleSuccess(state, action)
        goToNextSearchPage()
      },
    })
  }

  render() {
    const { handleSearchChange, queryParams, recommendations } = this.props

    const { search } = queryParams || {}

    return (
      <Main
        handleDataRequest={this.handleDataRequest}
        header={renderPageHeader}
        name="search"
        footer={renderPageFooter}
        redBg
      >
        <div>
          <form className="section" onSubmit={handleSearchChange}>
            <label className="label" id="search" htmlFor="search">
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
        <InfiniteScroller
          className="offers-list main-list"
          handleLoadMore={this.handleDataRequest}
        >
          {recommendations.map(o => (
            <SearchResultItem key={o.id} recommendation={o} />
          ))}
        </InfiniteScroller>
      </Main>
    )
  }
}

SearchPage.defaultProps = {
  querySearch: null,
}

SearchPage.propTypes = {
  goToNextSearchPage: PropTypes.func.isRequired,
  handleSearchChange: PropTypes.func.isRequired,
  queryParams: PropTypes.object.isRequired,
  querySearch: PropTypes.string,
  recommendations: PropTypes.array.isRequired,
  requestData: PropTypes.func.isRequired,
}

export default compose(
  withSearch({
    dataKey: 'recommendations',
    defaultQueryParams: {
      search: undefined,
    },
  }),
  connect(
    (state, ownProps) => {
      const queryParams = searchSelector(state, ownProps.location.search)
      return {
        queryParams,
        recommendations: selectRecommendations(state),
        user: state.user,
      }
    },
    { assignData, requestData, showModal }
  )
)(SearchPage)
