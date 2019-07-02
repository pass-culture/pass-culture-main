import PropTypes from 'prop-types'
import { showNotification } from 'pass-culture-shared'
import { stringify } from 'query-string'
import React, { Component, Fragment } from 'react'
import { Form } from 'react-final-form'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { NavLink } from 'react-router-dom'
import { assignData, requestData } from 'redux-saga-data'

import OffererItemContainer from './OffererItem/OffererItemContainer'
import PendingOffererItem from './PendingOffererItem'
import HeroSection from '../../layout/HeroSection'
import Icon from '../../layout/Icon'
import Main from '../../layout/Main'
import Spinner from '../../layout/Spinner'
import { TextField } from '../../layout/form/fields'
import { offererNormalizer } from '../../../utils/normalizers'
import {
  mapApiToBrowser,
  translateQueryParamsToApiParams,
} from '../../../utils/translate'

import createVenueForOffererUrl from './utils'

class Offerers extends Component {
  constructor(props) {
    super(props)
    const { dispatch } = props

    this.state = {
      hasMore: false,
      isLoading: false,
    }

    dispatch(assignData({ offerers: [], pendingOfferers: [] }))
  }

  componentDidMount() {
    this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { location } = this.props
    if (location.search !== prevProps.location.search) {
      this.handleRequestData()
    }
  }

  showNotification = (url) => {
    const { dispatch } = this.props
    dispatch(
      showNotification({
        tag: 'offerers',
        text: 'Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)',
        type: 'info',
        url: url,
        urlLabel: 'Nouveau lieu'
      })
    )
  }

  handleSuccess = (state, action) => {
    const {
      payload: { data },
    } = action
    this.setState({
      hasMore: data.length > 0,
      isLoading: false,
    })
  }


  handleRequestData = (handleSuccess, handleFail) => {
    const { currentUser, dispatch, offerers, query } = this.props
    const { isAdmin } = currentUser || {}
    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const apiParamsString = stringify(apiParams)
    const apiPath = `/offerers?${apiParamsString}`

    handleFail = () => {
      this.setState({
        hasMore: false,
        isLoading: false,
      })
    }

    this.setState({ isLoading: true }, () => {
      dispatch(
        requestData({
          apiPath,
          handleFail: handleFail(),
          handleSuccess: (state, action) => {
            const {
              payload: { data },
            } = action
            this.setState({
              hasMore: data.length > 0,
              isLoading: false,
            })
          },
          normalizer: offererNormalizer,
        })
      )
    })

    const url = createVenueForOffererUrl(offerers)
    const offerersHaveNotOffers = !currentUser.hasOffers
    const offerersHaveOnlyDigitalOffers = currentUser.hasOffers && !currentUser.hasPhysicalVenues

    const userHasNoOffersInAPhysicalVenueYet = offerersHaveNotOffers || offerersHaveOnlyDigitalOffers

    if (userHasNoOffersInAPhysicalVenueYet) {
       this.showNotification(url)
    }

    if (!isAdmin) {
      const notValidatedUserOfferersParams = Object.assign(
        {
          validated: false,
        },
        apiParams
      )
      const notValidatedUserOfferersSearch = stringify(
        notValidatedUserOfferersParams
      )
      const notValidatedUserOfferersPath = `/offerers?${notValidatedUserOfferersSearch}`
      dispatch(
        requestData({
          apiPath: notValidatedUserOfferersPath,
          normalizer: offererNormalizer,
          stateKey: 'pendingOfferers',
        })
      )
    }
  }

  onKeywordsSubmit = values => {
    const { dispatch, query } = this.props
    const { keywords } = values

    const isEmptyKeywords = typeof keywords === 'undefined' || keywords === ''

    if (!isEmptyKeywords) {
      dispatch(assignData({ offerers: [], pendingOfferers: [] }))
    }

    query.change({
      [mapApiToBrowser.keywords]: isEmptyKeywords ? null : keywords,
      page: null,
    })
  }

  render() {
    const { pendingOfferers, offerers, query } = this.props
    const queryParams = query.parse()
    const { hasMore, isLoading } = this.state


    const sectionTitle =
      offerers.length > 1
        ? 'Vos structures juridiques'
        : 'Votre structure juridique'

    const initialValues = {
      keywords: queryParams[mapApiToBrowser.keywords],
    }

    const url = createVenueForOffererUrl(offerers)

    return (
      <Main name="offerers">
        <HeroSection title={sectionTitle}>
          <p className="subtitle">
            Pour présenter vos offres, vous devez d'abord <a href={url}>créer un{' '}
            nouveau lieu </a> lié à une structure.
            <br />
            Sans lieu, vous pouvez uniquement <a href="/offres/creation">ajouter des offres numériques.</a>
          </p>
          <div className="title-action-links">
            <NavLink
              to="/structures/creation"
              className="cta button is-primary is-outlined">
              + Ajouter une structure
              <span
                className="tip-icon"
                data-place="bottom"
                data-tip="<p>Ajouter les SIREN des structures que vous souhaitez gérer au global avec ce compte (par exmple, un réseau de grande distribution ou de franchisés).</p>"
                data-type="info">
                <Icon svg="picto-tip" />
              </span>
            </NavLink>
          </div>
        </HeroSection>

        <Form
          initialValues={initialValues}
          onSubmit={this.onKeywordsSubmit}
          render={({ handleSubmit }) => (
            <form onSubmit={handleSubmit}>
              Rechercher une structure :
              <TextField
                id="search"
                name="keywords"
                placeholder="Saisissez un ou plusieurs mots complets"
                renderValue={() => (
                  <Fragment>
                    <button
                      className="button is-primary is-outlined search-ok ml12"
                      type="submit">
                      OK
                    </button>
                    <button className="button is-secondary" disabled>
                      &nbsp;
                      <Icon svg="ico-filter" />
                      &nbsp;
                    </button>
                  </Fragment>
                )}
              />
            </form>
          )}
        />

        <br />

        {pendingOfferers.length > 0 && (
          <ul id="pending-offerer-list" className="main-list offerers-list">
            {pendingOfferers.map(o => (
              <PendingOffererItem key={o.siren} offerer={o} />
            ))}
          </ul>
        )}

        <LoadingInfiniteScroll
          className="main-list offerers-list"
          element="ul"
          hasMore={hasMore}
          loader={<Spinner key="spinner" />}
          isLoading={isLoading}
          useWindow>
          {offerers.map(offerer => (
            <OffererItemContainer key={offerer.id} offerer={offerer} />
          ))}
        </LoadingInfiniteScroll>
      </Main>
    )
  }
}

PropTypes.propTypes = {
  currentUser: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
  query: PropTypes.object.isRequired,
}

export default Offerers
