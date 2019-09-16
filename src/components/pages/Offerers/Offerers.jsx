import PropTypes from 'prop-types'
import { stringify } from 'query-string'
import React, { Component, Fragment } from 'react'
import { Form } from 'react-final-form'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { NavLink } from 'react-router-dom'

import OffererItemContainer from './OffererItem/OffererItemContainer'
import PendingOffererItem from './OffererItem/PendingOffererItem'
import HeroSection from '../../layout/HeroSection/HeroSection'
import Icon from '../../layout/Icon'
import Main from '../../layout/Main'
import Spinner from '../../layout/Spinner'
import TextField from '../../layout/form/fields/TextField'
import { mapApiToBrowser, translateQueryParamsToApiParams } from '../../../utils/translate'
import createVenueForOffererUrl from './utils/createVenueForOffererUrl'
import userHasNoOffersInAPhysicalVenueYet from './utils/userHasNoOffersInAPhysicalVenueYet'

class Offerers extends Component {
  constructor(props) {
    super(props)
    const { resetLoadedOfferers } = props

    this.state = {
      hasMore: false,
      isLoading: false,
    }

    resetLoadedOfferers()
  }

  componentDidMount() {
    const { currentUser, offerers, showNotification } = this.props

    const url = createVenueForOffererUrl(offerers)

    if (userHasNoOffersInAPhysicalVenueYet(currentUser)) {
      showNotification(url)
    }

    this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { location, offerers } = this.props
    const numberOfOfferersPerLoad = 10
    const offerersHasBeenLoaded = offerers.length > prevProps.offerers.length

    if (offerersHasBeenLoaded) {
      this.scrollerIsNotLoading()

      const allOfferersLoaded = offerers.length !== prevProps.offerers.length + numberOfOfferersPerLoad
      if (allOfferersLoaded) {
        this.noMoreDataToLoad()
      }
    }

    const { hasMore } = this.state

    if (location.search !== prevProps.location.search && hasMore) {
      this.handleRequestData()
    }
  }

  componentWillUnmount() {
    const { closeNotification, notification } = this.props
    if (notification && notification.tag === 'offerers') {
      closeNotification()
    }
  }

  scrollerIsNotLoading = () => {
    this.setState({ isLoading: false })
  }

  noMoreDataToLoad = () => {
    this.setState({ hasMore: false })
  }

  handleFail = () => {
    this.setState({
      hasMore: false,
      isLoading: false,
    })
  }

  handleSuccess = () => {}

  handleRequestData = () => {
    const { currentUser, loadOfferers, query } = this.props

    const queryParams = query.parse()
    const apiParams = translateQueryParamsToApiParams(queryParams)
    const apiParamsString = stringify(apiParams)

    let loadOffererParameters = {
      keywords: apiParamsString,
    }

    if (currentUser.isAdmin === true) {
      loadOffererParameters.isValidated = true
    }

    this.setState(
      { isLoading: true, hasMore: true },
      loadOfferers(this.handleSuccess, this.handleFail, loadOffererParameters)
    )
  }

  handleOnKeywordsSubmit = values => {
    const { assignData, query } = this.props
    const { keywords } = values

    const isEmptyKeywords = typeof keywords === 'undefined' || keywords === ''

    assignData()

    query.change({
      [mapApiToBrowser.keywords]: isEmptyKeywords ? null : keywords,
      page: null,
    })
  }

  renderTextField = () => (
    <Fragment>
      <button
        className="button is-primary is-outlined search-ok ml12"
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
        <Icon svg="ico-filter" />
        &nbsp;
      </button>
    </Fragment>
  )

  renderForm = ({ handleSubmit }) => (
    <form onSubmit={handleSubmit}>
      {'Rechercher une structure :'}
      <TextField
        id="search"
        name="keywords"
        placeholder="Saisissez un ou plusieurs mots complets"
        renderValue={this.renderTextField}
      />
    </form>
  )

  render() {
    const { offerers, query } = this.props
    const queryParams = query.parse()
    const { hasMore, isLoading } = this.state

    const sectionTitle =
      offerers.length > 1 ? 'Vos structures juridiques' : 'Votre structure juridique'

    const initialValues = {
      keywords: queryParams[mapApiToBrowser.keywords],
    }

    const url = createVenueForOffererUrl(offerers)

    return (
      <Main
        id="offerers"
        name="offerers"
      >
        <HeroSection title={sectionTitle}>
          <p className="subtitle">
            {'Pour présenter vos offres, vous devez d’abord '}
            <a href={url}>
              {'créer un nouveau lieu '}
            </a>
            {' lié à une structure.'}
            <br />
            {'Sans lieu, vous pouvez uniquement '}
            <a href="/offres/creation">
              {'ajouter des offres numériques.'}
            </a>
          </p>
          <div className="title-action-links">
            <NavLink
              className="cta button is-primary is-outlined"
              to="/structures/creation"
            >
              {'+ Ajouter une structure'}
              <span
                className="tip-icon"
                data-place="bottom"
                data-tip="<p>Ajouter les SIREN des structures que vous souhaitez gérer au global avec ce compte (par exemple, un réseau de grande distribution ou de franchisés).</p>"
                data-type="info"
              >
                <Icon svg="picto-tip" />
              </span>
            </NavLink>
          </div>
        </HeroSection>

        <Form
          initialValues={initialValues}
          onSubmit={this.handleOnKeywordsSubmit}
          render={this.renderForm}
        />

        <br />

        <LoadingInfiniteScroll
          className="main-list offerers-list"
          element="ul"
          hasMore={hasMore}
          isLoading={isLoading}
          loader={<Spinner key="spinner" />}
        >
          {offerers.map(offerer => {
            return offerer.isValidated && offerer.userHasAccess ? (
              <OffererItemContainer
                key={offerer.id}
                offerer={offerer}
              />
            ) : (
              <PendingOffererItem
                key={offerer.siren}
                offerer={offerer}
              />
            )
          })}
        </LoadingInfiniteScroll>
      </Main>
    )
  }
}

Offerers.propTypes = {
  assignData: PropTypes.func.isRequired,
  closeNotification: PropTypes.func.isRequired,
  currentUser: PropTypes.shape().isRequired,
  loadOfferers: PropTypes.func.isRequired,
  offerers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  query: PropTypes.shape().isRequired,
  resetLoadedOfferers: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
}

export default Offerers
