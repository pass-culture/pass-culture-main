import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import {
  assignData,
  Icon,
  Logger,
  requestData,
  resolveIsNew,
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

// eslint-disable-resolveIsNew jsx-a11y/label-has-for

class SearchPage extends Component {
  // handleDataRequest = () => 'data'
  componentDidMount() {
    Logger.log('DiscoveryPage ---> componentDidMount')
  }

  componentWillUnmount() {
    Logger.log('DiscoveryPage ---> componentWillUnmount')
  }

  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { goToNextSearchPage, querySearch } = this.props
    requestData('GET', `recommendations?${querySearch}`, {
      handleFail,
      handleSuccess: (state, action) => {
        handleSuccess(state, action)
        goToNextSearchPage()
      },
      resolve: resolveIsNew,
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
            {/* <label className="label" id="search"> */}
            <p className="label" id="search">
              Rechercher une offre :
            </p>
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
          {recommendations.map(item => (
            <SearchResultItem key={item.id} recommendation={item} />
            // TODO SearchResultItem based on booking so for events only
          ))}
        </ul>
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
  // requestData: PropTypes.func.isRequired,
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
