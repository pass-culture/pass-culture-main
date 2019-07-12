import { Icon, resolveIsNew } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Component } from 'react'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { NavLink } from 'react-router-dom'
import { assignData, requestData } from 'redux-saga-data'

import OfferItemContainer from './OfferItem/OfferItemContainer'
import HeroSection from '../../layout/HeroSection/HeroSection'
import Spinner from '../../layout/Spinner'
import Main from '../../layout/Main'
import { offerNormalizer } from '../../../utils/normalizers'
import { mapApiToBrowser, translateQueryParamsToApiParams } from '../../../utils/translate'

class RawOffers extends Component {
  constructor(props) {
    super(props)

    this.state = {
      hasMore: false,
      isLoading: false,
    }
    props.dispatch(assignData({ offers: [] }))
  }

  componentDidMount() {
    const { query } = this.props
    const queryParams = query.parse()
    if (queryParams.page) {
      query.change({ page: null })
    } else {
      this.onHandleRequestData()
    }
  }

  componentDidUpdate(prevProps) {
    const { location } = this.props
    if (location.search !== prevProps.location.search) {
      this.onHandleRequestData()
    }
  }

  onHandleRequestData = () => {
    const { comparedTo, dispatch, query, types } = this.props

    types.length === 0 && dispatch(requestData({ apiPath: '/types' }))

    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const apiParamsString = stringify(apiParams)
    const apiPath = `/offers?${apiParamsString}`

    this.setState({ isLoading: true }, () => {
      dispatch(
        requestData({
          apiPath,
          handleFail: () => {
            this.setState({
              hasMore: false,
              isLoading: false,
            })
          },
          handleSuccess: (state, action) => {
            const {
              payload: { data },
            } = action
            this.setState({
              hasMore: data.length > 0,
              isLoading: false,
            })
          },
          normalizer: offerNormalizer,
          resolve: datum => resolveIsNew(datum, 'dateCreated', comparedTo),
        })
      )
    })
  }

  handleOnSubmit = event => {
    event.preventDefault()
    const { dispatch, query } = this.props
    const value = event.target.elements.search.value
    const isEmptySearch = typeof value === 'undefined' || value === ''

    query.change({
      [mapApiToBrowser.keywords]: value === '' ? null : value,
      page: null,
    })

    if (!isEmptySearch) {
      dispatch(assignData({ offers: [] }))
    }
  }

  handleOnVenueClick = query => () => {
    query.change({
      [mapApiToBrowser.venueId]: null,
      page: null,
    })
  }

  handleOnOffererClick = query => () => {
    query.change({
      [mapApiToBrowser.offererId]: null,
      page: null,
    })
  }

  handleOnClick = () => {
    // TODO
    // query.change({ })}
  }

  handleOnChange = () => {
    // TODO pagination.orderBy
    // query.change({})
  }

  render() {
    const { currentUser, offers, offerer, query, venue } = this.props
    const { isAdmin } = currentUser || {}

    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const { keywords, venueId, offererId, orderBy } = apiParams

    const { hasMore, isLoading } = this.state

    let createOfferTo = `/offres/creation`
    if (venueId) {
      createOfferTo = `${createOfferTo}?${mapApiToBrowser.venueId}=${venueId}`
    } else if (offererId) {
      createOfferTo = `${createOfferTo}?${mapApiToBrowser.offererId}=${offererId}`
    }

    const [orderName, orderDirection] = (orderBy || '').split('+')

    return (
      <Main
        handleRequestData={this.onHandleRequestData}
        name="offers"
      >
        <HeroSection title="Vos offres">
          {!isAdmin && (
            <NavLink
              className="cta button is-primary"
              to={createOfferTo}
            >
              <span className="icon">
                <Icon svg="ico-offres-w" />
              </span>
              <span>{'Créer une offre'}</span>
            </NavLink>
          )}
        </HeroSection>
        <form
          className="section"
          onSubmit={this.handleOnSubmit}
        >
          <label className="label">{'Rechercher une offre :'}</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                className="input"
                defaultValue={keywords}
                id="search"
                placeholder="Saisissez un ou plusieurs mots complets"
                type="text"
              />
            </p>
            <p className="control">
              <button
                className="button is-primary is-outlined"
                id="search-button"
                type="submit"
              >
                {'OK'}
              </button>
              <button
                className="button is-secondary"
                disabled
                type="button"
              >
                &nbsp;
                &nbsp;
                <Icon svg="ico-filter" />
              </button>
            </p>
          </div>
        </form>

        <ul className="section">
          {offerer ? (
            <li className="tag is-rounded is-medium">
              {'Structure :'}
              <span className="has-text-weight-semibold">&nbsp;{offerer.name}</span>
              <button
                className="delete is-small"
                onClick={this.handleOnOffererClick(query)}
                type="button"
              />
            </li>
          ) : (
            venue && (
              <li className="tag is-rounded is-medium">
                {'Lieu : '}
                <span className="has-text-weight-semibold">{venue.name}</span>
                <button
                  className="delete is-small"
                  onClick={this.handleOnVenueClick(query)}
                  type="button"
                />
              </li>
            )
          )}
        </ul>
        <div className="section">
          {false && (
            <div className="list-header">
              <div>
                <div className="recently-added" />
                {'Ajouté récemment'}
              </div>
              <div>
                {'Trier par: '}
                <span className="select is-rounded is-small">
                  <select
                    onBlur={this.handleOnChange}
                    value={orderName}
                  >
                    <option value="sold">{'Offres écoulées'}</option>
                    <option value="createdAt">{'Date de création'}</option>
                  </select>
                </span>
              </div>
              <div>
                <button
                  className="button is-secondary"
                  onClick={this.handleOnClick}
                  type="button"
                >
                  <Icon
                    svg={orderDirection === 'asc' ? 'ico-sort-ascending' : 'ico-sort-descending'}
                  />
                </button>
              </div>
            </div>
          )}
          <LoadingInfiniteScroll
            className="offers-list main-list"
            element="ul"
            hasMore={hasMore}
            isLoading={isLoading}
            loader={<Spinner key="spinner" />}
            useWindow
          >
            {offers.map(offer => (
              <OfferItemContainer
                key={offer.id}
                offer={offer}
              />
            ))}
          </LoadingInfiniteScroll>
        </div>
      </Main>
    )
  }
}

RawOffers.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  offers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default RawOffers
