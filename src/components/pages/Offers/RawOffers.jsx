import { Icon, resolveIsNew } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Component } from 'react'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { NavLink } from 'react-router-dom'
import { assignData, requestData } from 'redux-saga-data'

import OfferItem from './OfferItem'
import HeroSection from '../../layout/HeroSection'
import Spinner from '../../layout/Spinner'
import Main from '../../layout/Main'
import { offerNormalizer } from '../../../utils/normalizers'
import {
  mapApiToBrowser,
  translateBrowserUrlToApiUrl,
} from '../../../utils/translate'

class RawOffers extends Component {
  constructor(props) {
    super(props)

    const { query } = props
    const queryParams = query.parse()
    this.state = {
      hasMore: false,
      keywordsValue: queryParams[mapApiToBrowser.keywords],
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
      this.handleRequestData()
    }
  }

  componentDidUpdate(prevProps) {
    const { location } = this.props
    if (location.search !== prevProps.location.search) {
      this.handleRequestData()
    }
  }

  handleRequestData = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { comparedTo, dispatch, query, types } = this.props

    types.length === 0 && dispatch(requestData({ apiPath: '/types' }))

    const queryParams = query.parse()
    const apiParams = translateBrowserUrlToApiUrl(queryParams)
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

  onSubmit = event => {
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

  render() {
    const {
      currentUser,
      offers,
      offerer,
      pagination,
      query,
      venue,
    } = this.props
    const { isAdmin } = currentUser || {}
    const queryParams = query.parse()
    const apiParams = translateBrowserUrlToApiUrl(queryParams)
    const { keywords, venueId, offererId, orderBy } = apiParams

    const { hasMore, isLoading } = this.state

    let createOfferTo = `/offres/nouveau`
    if (venueId) {
      createOfferTo = `${createOfferTo}?${mapApiToBrowser.venueId}=${venueId}`
    } else if (offererId) {
      createOfferTo = `${createOfferTo}?${
        mapApiToBrowser.offererId
      }=${offererId}`
    }

    const [orderName, orderDirection] = (orderBy || '').split('+')

    return (
      <Main handleRequestData={this.handleRequestData} name="offers">
        <HeroSection title="Vos offres">
          {!isAdmin && (
            <NavLink to={createOfferTo} className="cta button is-primary">
              <span className="icon">
                <Icon svg="ico-offres-w" />
              </span>
              <span>Créer une offre</span>
            </NavLink>
          )}
        </HeroSection>
        <form className="section" onSubmit={this.onSubmit}>
          <label className="label">Rechercher une offre :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                id="search"
                className="input"
                placeholder="Saisissez un ou plusieurs mots complets"
                type="text"
                defaultValue={keywords}
              />
            </p>
            <p className="control">
              <button
                type="submit"
                className="button is-primary is-outlined"
                id="search-button">
                OK
              </button>{' '}
              <button className="button is-secondary" disabled>
                &nbsp;
                <Icon svg="ico-filter" />
                &nbsp;
              </button>
            </p>
          </div>
        </form>

        <ul className="section">
          {offerer ? (
            <li className="tag is-rounded is-medium">
              Structure :
              <span className="has-text-weight-semibold"> {offerer.name} </span>
              <button
                className="delete is-small"
                onClick={() =>
                  query.change({
                    [mapApiToBrowser.offererId]: null,
                    page: null,
                  })
                }
              />
            </li>
          ) : (
            venue && (
              <li className="tag is-rounded is-medium">
                Lieu :
                <span className="has-text-weight-semibold">{venue.name}</span>
                <button
                  className="delete is-small"
                  onClick={() =>
                    query.change({
                      [mapApiToBrowser.venueId]: null,
                      page: null,
                    })
                  }
                />
              </li>
            )
          )}
        </ul>
        <div className="section">
          {// TODO pagination.orderBy & pagination.reverseOrder are broken, replace by new implementation with withQueryRouter
          false && (
            <div className="list-header">
              <div>
                <div className="recently-added" />
                Ajouté récemment
              </div>
              <div>
                Trier par:
                <span className="select is-rounded is-small">
                  <select
                    onChange={pagination.orderBy}
                    className=""
                    value={orderName}>
                    <option value="sold">Offres écoulées</option>
                    <option value="createdAt">Date de création</option>
                  </select>
                </span>
              </div>
              <div>
                <button
                  onClick={pagination.reverseOrder}
                  className="button is-secondary">
                  <Icon
                    svg={
                      orderDirection === 'asc'
                        ? 'ico-sort-ascending'
                        : 'ico-sort-descending'
                    }
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
            useWindow>
            {offers.map(offer => (
              <OfferItem key={offer.id} offer={offer} />
            ))}
          </LoadingInfiniteScroll>
        </div>
      </Main>
    )
  }
}

RawOffers.propTypes = {
  currentUser: PropTypes.object.isRequired,
  offers: PropTypes.array,
}

export default RawOffers
