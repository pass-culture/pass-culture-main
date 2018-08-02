import {
  assignData,
  Icon,
  InfiniteScroller,
  requestData,
  showModal,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import OfferItem from '../OfferItem'
import Main from '../layout/Main'
import offersSelector from '../../selectors/offers'
import offererSelector from '../../selectors/offerer'
import searchSelector from '../../selectors/search'
import venueSelector from '../../selectors/venue'
import { offerNormalizer } from '../../utils/normalizers'
import { objectToQueryString } from '../../utils/string'

const ASC = 'asc'
const DESC = 'desc'

const defaultQueryParams = {
  search: undefined,
  order_by: `createdAt+${DESC}`,
  venueId: null,
  offererId: null,
}

class OffersPage extends Component {
  constructor() {
    super()
    this.state = {
      queryParams: defaultQueryParams,
      page: 1,
    }
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const queryParams = Object.assign(
      {},
      defaultQueryParams,
      nextProps.queryParams
    )

    return {
      queryParams,
      page: prevState.page,
    }
  }

  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { requestData, types } = this.props
    requestData(
      'GET',
      `offers?${objectToQueryString(
        Object.assign({}, this.state.queryParams, { page: this.state.page })
      )}`,
      {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          this.setState({
            page: this.state.page + 1,
          })
        },
        handleFail,
        normalizer: offerNormalizer,
      }
    )
    types.length === 0 && requestData('GET', 'types')
  }

  handleQueryParamsChange(newValue) {
    const newPath = `${this.props.location.pathname}?${objectToQueryString(
      Object.assign({}, this.state.queryParams, newValue)
    )}`
    this.props.assignData({ offers: [] })
    this.setState({
      page: 1,
    })
    this.props.history.push(newPath)
  }

  handleOrderDirectionChange = e => {
    const [by, direction] = this.state.queryParams.order_by.split('+')
    this.handleQueryParamsChange({
      order_by: [by, direction === DESC ? ASC : DESC].join('+'),
    })
  }

  handleOrderByChange = e => {
    const [, direction] = this.state.queryParams.order_by.split('+')
    this.handleQueryParamsChange({
      order_by: [e.target.value, direction].join('+'),
    })
  }

  handleRemoveFilter = key => e => {
    this.handleQueryParamsChange({ [key]: null })
  }

  handleSearchChange = e => {
    e.preventDefault()
    this.handleQueryParamsChange({ search: e.target.elements.search.value })
  }

  render() {
    const { offers, offerer, venue } = this.props

    const { search, order_by } = this.state.queryParams || {}

    const [orderBy, orderDirection] = order_by.split('+')
    return (
      <Main name="offers" handleDataRequest={this.handleDataRequest}>
        <div className="section">
          <NavLink
            to={`/offres/nouveau`}
            className="button is-primary is-medium is-pulled-right">
            <span className="icon">
              <Icon svg="ico-offres-w" />
            </span>
            <span>Créer une offre</span>
          </NavLink>
          <h1 className="main-title">Vos offres</h1>
        </div>
        <form className="section" onSubmit={this.handleSearchChange}>
          <label className="label">Rechercher une offre :</label>
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
              </button>{' '}
              <button className="button is-secondary">
                &nbsp;<Icon svg="ico-filter" />&nbsp;
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
                onClick={this.handleRemoveFilter('offererId')}
              />
            </li>
          ) : (
            venue && (
              <li className="tag is-rounded is-medium">
                Lieu :
                <span className="has-text-weight-semibold">{venue.name}</span>
                <button
                  className="delete is-small"
                  onClick={this.handleRemoveFilter('venueId')}
                />
              </li>
            )
          )}
        </ul>

        {
          <div className="section">
            <div className="list-header">
              <div>
                <div className="recently-added" />
                Ajouté récemment
              </div>
              <div>
                Trier par:
                <span className="select is-rounded is-small">
                  <select
                    onChange={this.handleOrderByChange}
                    className=""
                    value={orderBy}>
                    <option value="sold">Offres écoulées</option>
                    <option value="createdAt">Date de création</option>
                  </select>
                </span>
              </div>
              <div>
                <button
                  onClick={this.handleOrderDirectionChange}
                  className="button is-secondary">
                  <Icon
                    svg={
                      orderDirection === ASC
                        ? 'ico-sort-ascending'
                        : 'ico-sort-descending'
                    }
                  />
                </button>
              </div>
            </div>
            {
              <InfiniteScroller
                className="offers-list main-list"
                handleLoadMore={this.handleDataRequest}>
                {offers.map(o => <OfferItem key={o.id} offer={o} />)}
              </InfiniteScroller>
            }
          </div>
        }
      </Main>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const queryParams = searchSelector(state, ownProps.location.search)
      return {
        offers: offersSelector(
          state,
          queryParams.offererId,
          queryParams.venueId
        ),
        offerer: offererSelector(state, queryParams.offererId),
        queryParams,
        user: state.user,
        types: state.data.types,
        venue: venueSelector(state, queryParams.venueId),
      }
    },
    { showModal, requestData, assignData }
  )
)(OffersPage)
