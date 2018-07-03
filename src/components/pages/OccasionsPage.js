import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import OccasionItem from '../OccasionItem'
import InfiniteScroller from '../layout/InfiniteScroller'
import Icon from '../layout/Icon'
import Search from '../layout/Search'
import PageWrapper from '../layout/PageWrapper'
import { showModal } from '../../reducers/modal'
import { requestData } from '../../reducers/data'
import createOccasionsSelector from '../../selectors/createOccasions'
import createOffererSelector from '../../selectors/createOfferer'
import createSearchSelector from '../../selectors/createSearch'
import createVenueSelector from '../../selectors/createVenue'
import { occasionNormalizer } from '../../utils/normalizers'
import { queryStringToObject, objectToQueryString } from '../../utils/string'

const ASC = 'asc'
const DESC = 'desc'

const defaultSearch = {
  orderBy: 'date',
  orderDirection: DESC,
  q: null,
  venueId: null,
  offererId: null,
}

class OccasionsPage extends Component {

  constructor() {
    super()
    this.state = {
      search: defaultSearch,
      occasions: [],
    }
  }

  static getDerivedStateFromProps(nextProps) {
    const search = Object.assign({}, defaultSearch, queryStringToObject(nextProps.location.search))
    return {
      search,
      occasions: nextProps.occasions
        .sort((o1, o2) => ((o1[search.orderBy] - o2[search.orderBy]) * (search.orderDirection === DESC ? 1 : -1)))
    }
  }

  handleDataRequest = (handleSuccess=()=>{}, handleFail=()=>{}, page=1) => {
    const {
      offererId,
      requestData,
      user,
      types,
      venueId
    } = this.props
    let apiPath = 'occasions?'
    if (venueId) {
      apiPath = `${apiPath}venueId=${venueId}&`
    } else if (offererId) {
      apiPath = `${apiPath}offererId=${offererId}&`
    }
    user && requestData(
      'GET',
      `${apiPath}page=${page}`,
      {
        handleSuccess,
        handleFail,
        normalizer: occasionNormalizer
      }
    )
    types.length === 0 && requestData('GET', 'types')
  }

  handleSearchChange(newValue) {
    console.log('path', this.props.location)
    const newPath = `${this.props.location.pathname}?${objectToQueryString(Object.assign({}, this.state.search, newValue))}`
    console.log('newPath', newPath)
    this.props.history.push(newPath)
  }

  handleOrderDirectionChange = e => {
    this.handleSearchChange({orderDirection: this.state.search.orderDirection === DESC ? ASC : DESC })
  }

  handleOrderByChange = e => {
    this.handleSearchChange({orderBy: e.target.value})
  }

  handleQueryChange = e => {
    this.handleSearchChange({q: e.target.value})
  }

  handleRemoveFilter = key => e => {
    this.handleSearchChange({[key]: null})
  }

  render() {
    const {
      occasions,
      offerer,
      venue,
    } = this.props

    const {
      orderBy,
      orderDirection,
      q,
    } = this.state.search || {}

    console.log(this.state.search)

    return (
      <PageWrapper name="offers" handleDataRequest={this.handleDataRequest}>
        <div className="section">
          <NavLink to={`/offres/nouveau`} className='button is-primary is-medium is-pulled-right'>
            <span className='icon'><Icon svg='ico-offres-w' /></span>
            <span>Créer une offre</span>
          </NavLink>
          <h1 className='pc-title'>
            Vos offres
          </h1>
        </div>
        <div className='section'>
          <label className="label">Rechercher une offre :</label>
          <Search collectionName="occasions"
                  config={{
                    isMergingArray: false,
                    key: 'searchedOccasions'
                  }}
          />
        </div>

        <ul className='section'>
          {
            offerer
              ? (
                <li className='tag is-rounded is-medium'>
                  Structure :
                  <span className="has-text-weight-semibold"> {offerer.name} </span>
                  <button class="delete is-small" onClick={this.handleRemoveFilter('offererId')}></button>
                </li>
              )
              : venue && (
                <li className='tag is-rounded is-medium'>
                  Lieu :
                  <span className="has-text-weight-semibold"> {venue.name} </span>
                  <button class="delete is-small" onClick={this.handleRemoveFilter('venueId')}></button>
                </li>
              )
          }
        </ul>

        {
          <div className='section'>
            <div className='list-header'>
              <div>
                <div className='recently-added'></div>
                Ajouté récemment
              </div>
              <div>
                Trier par:
                <span className='select is-rounded is-small'>
                <select onChange={this.handleOrderByChange} className=''>
                  <option value='sold'>Offres écoulées</option>
                  <option value='createdAt'>Date de création</option>
                </select>
                </span>
              </div>
              <div>
                <button onClick={this.handleOrderDirectionChange} className='button is-secondary'>
                  <Icon svg={orderDirection === ASC ? 'ico-sort-ascending' : 'ico-sort-descending'} />
                </button>
              </div>
            </div>
            <InfiniteScroller className='occasions-list pc-list' handleLoadMore={this.handleDataRequest}>
              { occasions.map(o =>
                <OccasionItem key={o.id} occasion={o} />
              )}
            </InfiniteScroller>
          </div>
        }
      </PageWrapper>
    )
  }
}


const occasionsSelector = createOccasionsSelector()
const offererSelector = createOffererSelector()
const searchSelector = createSearchSelector()
const venueSelector = createVenueSelector()

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { offererId, venueId } = searchSelector(state, ownProps.location.search)
      return {
        occasions: occasionsSelector(state, offererId, venueId),
        offerer: offererSelector(state, offererId),
        offererId,
        user: state.user,
        types: state.data.types,
        venue: venueSelector(state, venueId),
        venueId
      }
    },
    { showModal, requestData }
  )
)(OccasionsPage)
