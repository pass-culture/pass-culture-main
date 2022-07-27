/*eslint no-undef: 0*/
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import LoadingInfiniteScroll from 'react-loading-infinite-scroller'
import { Link, useHistory, useLocation } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { ReactComponent as AddOffererSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'
import { mapApiToBrowser } from 'utils/translate'

import OffererItemContainer from './OffererItem/OffererItemContainer'
import PendingOffererItem from './OffererItem/PendingOffererItem'
import createVenueForOffererUrl from './utils/createVenueForOffererUrl'

/* eslint-disable */
function withRouter(Component) {
  return props => (
    <Component {...props} history={useHistory()} location={useLocation()} />
  )
}
/* eslint-enable */

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
// TO FIX:: the above component is temporary, in order to
// allow react-router upgrade before the below component is refactored as function component
class Offerers extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      hasMore: false,
      isLoading: false,
      keywordsInputValue: '',
      offerers: [],
    }
  }

  componentDidMount() {
    // We need to use this system because of this issue:
    // https://github.com/danbovey/react-infinite-scroller/issues/12#issuecomment-339375017
    this.forceRenderKey = 0

    this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { location } = this.props

    if (location.search !== prevProps.location.search) {
      this.handleRequestData()
    }
  }

  changeKeywordsValue = event => {
    this.setState({ keywordsInputValue: event.target.value })
  }

  handleGetOfferersSuccess = getOfferersResponse => {
    const { offerers } = this.state

    // TODO (rlecellier): This should be remove after MEP 177 when route serializer alwayse return a object
    const isOldApi = Array.isArray(getOfferersResponse)
    const fetchedOfferers = isOldApi
      ? getOfferersResponse
      : getOfferersResponse.offerers
    const nbTotalResults = isOldApi ? 100 : getOfferersResponse.nbTotalResults
    const newOfferers = [...offerers, ...fetchedOfferers]
    this.setState({
      hasMore: newOfferers.length < nbTotalResults,
      offerers: newOfferers,
      isLoading: false,
    })
  }

  handleGetOfferersFail = () => {
    this.setState({
      hasMore: false,
      isLoading: false,
    })
  }

  handleRequestData = async () => {
    this.setState({ isLoading: true, hasMore: true })
    const { location } = this.props
    const queryParams = new URLSearchParams(location.search)

    const searchKeyWords = queryParams.get('mots-cles')
      ? queryParams.get('mots-cles').split(' ')
      : []

    const filters = {
      keywords:
        typeof searchKeyWords === 'string' ? [searchKeyWords] : searchKeyWords,
      page: queryParams.get('page') || '1',
    }

    await pcapi
      .getOfferers(filters)
      .then(this.handleGetOfferersSuccess)
      .catch(this.handleGetOfferersFail)
  }

  handleOnKeywordsSubmit = () => {
    const { history, location } = this.props
    const { keywordsInputValue } = this.state
    const keywords = keywordsInputValue

    const queryParams = new URLSearchParams(location.search)

    history.replace('/structures?mots-cles=' + keywords || '')

    this.forceRenderKey++ // See variable declaration for more information

    if (queryParams[mapApiToBrowser.keywords] !== keywords)
      this.setState({ offerers: [] })
  }

  renderForm = ({ handleSubmit }) => {
    const { keywordsInputValue } = this.state

    return (
      <form className="form-search" onSubmit={handleSubmit}>
        <TextInput
          label="Rechercher une structure :"
          name="keywords"
          onChange={this.changeKeywordsValue}
          placeholder="Saisissez un ou plusieurs mots complets"
          value={keywordsInputValue}
        />
        <button className="secondary-button" type="submit">
          OK
        </button>
      </form>
    )
  }

  onPageChange = page => {
    const { history, location } = this.props
    const queryParams = new URLSearchParams(location.search)
    queryParams.set('page', page)
    history.replace(`structures?${queryParams.toString()}`)
  }

  onPageReset = () => {
    const { history, location } = this.props
    const queryParams = new URLSearchParams(location.search)
    queryParams.delete('page')
    history.replace(`structures?${queryParams.toString()}`)
  }

  render() {
    const { isOffererCreationAvailable, location } = this.props
    const queryParams = new URLSearchParams(location.search)
    const { hasMore, isLoading, offerers } = this.state
    const sectionTitle =
      offerers.length > 1 ? 'Structures juridiques' : 'Structure juridique'

    const initialValues = {
      keywords: queryParams[mapApiToBrowser.keywords],
    }

    const url = isOffererCreationAvailable
      ? createVenueForOffererUrl(offerers)
      : UNAVAILABLE_ERROR_PAGE

    const offererCreationPageURL = isOffererCreationAvailable
      ? '/structures/creation'
      : UNAVAILABLE_ERROR_PAGE

    const actionLink = (
      <span>
        <Link className="primary-button with-icon" to={offererCreationPageURL}>
          <AddOffererSvg />
          Ajouter une structure
        </Link>
        <Icon
          data-place="bottom"
          data-tip="<p>Ajouter les SIREN des structures que vous souhaitez gérer au global avec ce compte (par exemple, un réseau de grande distribution ou de franchisés).</p>"
          data-type="info"
          svg="picto-tip"
        />
      </span>
    )

    return (
      <div className="offerers-page">
        <PageTitle title="Vos structures juridiques" />
        <Titles action={actionLink} title={sectionTitle} />
        <p className="advice">
          Pour présenter vos offres, vous devez d’abord{' '}
          <a href={url}>créer un nouveau lieu</a> lié à une structure.
          <br />
          Sans lieu, vous pouvez uniquement ajouter des offres numériques.
        </p>

        <Form
          initialValues={initialValues}
          onSubmit={this.handleOnKeywordsSubmit}
          render={this.renderForm}
        />

        <br />

        <LoadingInfiniteScroll
          className="main-list offerers-list"
          element="ul"
          handlePageChange={this.onPageChange}
          handlePageReset={this.onPageReset}
          hasMore={hasMore}
          isLoading={isLoading}
          key={this.forceRenderKey} // See variable declaration for more information
          loader={<Spinner key="spinner" />}
        >
          {offerers.map(offerer => {
            return offerer.isValidated && offerer.userHasAccess ? (
              <OffererItemContainer key={offerer.id} offerer={offerer} />
            ) : (
              <PendingOffererItem key={offerer.siren} offerer={offerer} />
            )
          })}
        </LoadingInfiniteScroll>
        {hasMore === false && 'Fin des résultats'}
      </div>
    )
  }
}

Offerers.propTypes = {
  history: PropTypes.shape().isRequired,
  isOffererCreationAvailable: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
}

export default withRouter(Offerers)
