import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Component, Fragment } from 'react'
import { Form } from 'react-final-form'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { NavLink } from 'react-router-dom'
import { assignData, requestData } from 'redux-saga-data'

import OffererItem from './OffererItem'
import PendingOffererItem from './PendingOffererItem'
import HeroSection from '../../layout/HeroSection'
import Icon from '../../layout/Icon'
import Main from '../../layout/Main'
import Spinner from '../../layout/Spinner'
import { TextField } from '../../layout/form'
import { offererNormalizer } from '../../../utils/normalizers'
import {
  mapApiToBrowser,
  translateQueryParamsToApiParams,
} from '../../../utils/translate'

class RawOfferers extends Component {
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

  handleRequestData = (handleSuccess, handleFail) => {
    const { currentUser, dispatch, query } = this.props
    const { isAdmin } = currentUser || {}

    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const apiParamsString = stringify(apiParams)
    const apiPath = `/offerers?${apiParamsString}`

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
          normalizer: offererNormalizer,
        })
      )
    })

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

    return (
      <Main name="offerers">
        <HeroSection title={sectionTitle}>
          <p className="subtitle">
            Pour présenter vos offres, vous devez d'abord créer un{' '}
            <b> nouveau lieu </b> lié à une structure.
            <br />
            Sans lieu, vous ne pouvez ajouter que des offres numériques.
          </p>
          <NavLink
            to="/structures/nouveau"
            className="cta button is-primary is-outlined">
            + Rattacher une structure supplémentaire
          </NavLink>
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
            <OffererItem key={offerer.id} offerer={offerer} />
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

export default RawOfferers
