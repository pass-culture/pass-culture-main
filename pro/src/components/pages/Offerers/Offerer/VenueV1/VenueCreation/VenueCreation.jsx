/*eslint no-undef: 0*/
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { useDispatch, useSelector } from 'react-redux'
import { NavLink, useHistory, useLocation, useParams } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { unhumanizeSiret } from 'core/Venue/utils'
import {
  createVenue,
  getOfferer,
  getVenueLabels,
  getVenueTypes,
} from 'repository/pcapi/pcapi'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import ModifyOrCancelControl from '../controls/ModifyOrCancelControl/ModifyOrCancelControl'
import ReturnOrSubmitControl from '../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'
import AccessibilityFields, {
  autoFillNoDisabilityCompliantDecorator,
} from '../fields/AccessibilityFields'
import BankInformation from '../fields/BankInformationFields'
import BusinessUnitFields from '../fields/BankInformationFields/BusinessUnitFields'
import ContactInfosFields from '../fields/ContactInfosFields'
import IdentifierFields, {
  bindGetSiretInformationToSiret,
} from '../fields/IdentifierFields'
import LocationFields, {
  bindGetSuggestionsToLatitude,
  bindGetSuggestionsToLongitude,
  FRANCE_POSITION,
} from '../fields/LocationFields'
import WithdrawalDetailsFields from '../fields/WithdrawalDetailsFields'
import NotificationMessage from '../Notification'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import VenueType from '../ValueObjects/VenueType'

/* eslint-disable */
const withRouter = Component => {
  return props => (
    <Component
      {...props}
      currentUser={useSelector(state => selectCurrentUser(state))}
      dispatch={useDispatch()}
      history={useHistory()}
      isBankInformationWithSiretActive={useActiveFeature(
        'ENFORCE_BANK_INFORMATION_WITH_SIRET'
      )}
      isEntrepriseApiDisabled={useActiveFeature('DISABLE_ENTERPRISE_API')}
      location={useLocation()}
      params={useParams()}
    />
  )
}
/* eslint-enable */

// TO FIX:: the above component is temporary, in order to
// allow react-router upgrade before the below component is refactored as function component
class VenueCreation extends PureComponent {
  constructor(props) {
    super()
    const { offererId } = props.params
    this.state = {
      isReady: false,
      offerer: null,
      venueTypes: null,
      venueLabels: null,
      formInitialValues: {
        managingOffererId: offererId,
        bookingEmail: props.currentUser.email,
      },
      isBankInformationWithSiretActive: props.isBankInformationWithSiretActive,
      isEntrepriseApiDisabled: props.isEntrepriseApiDisabled,
    }
  }

  componentDidMount() {
    this.handleInitialRequest().then(({ offerer, venueTypes, venueLabels }) => {
      this.setState({
        isReady: true,
        offerer,
        venueTypes,
        venueLabels,
      })
    })
  }

  async handleInitialRequest() {
    const offererRequest = getOfferer(
      this.state.formInitialValues.managingOffererId
    )
    const venueTypesRequest = getVenueTypes().then(venueTypes => {
      return venueTypes.map(type => new VenueType(type))
    })
    const venueLabelsRequest = getVenueLabels().then(labels => {
      return [...labels].sort((a, b) => a.label.localeCompare(b.label, 'fr'))
    })
    const [offerer, venueTypes, venueLabels] = await Promise.all([
      offererRequest,
      venueTypesRequest,
      venueLabelsRequest,
    ])
    return {
      offerer,
      venueTypes,
      venueLabels,
    }
  }

  async handleSubmitRequest({ formValues, handleFail, handleSuccess }) {
    const body = formatVenuePayload(formValues, true)
    try {
      const response = await createVenue(body)
      handleSuccess(response)
    } catch (responseError) {
      handleFail(responseError)
    }
  }

  handleSubmitFailNotification(errors) {
    let text = 'Une ou plusieurs erreurs sont présentes dans le formulaire.'
    if (errors.global) {
      text = `${text} ${errors.global[0]}`
    }

    this.props.dispatch(
      showNotification({
        text,
        type: 'error',
      })
    )
  }

  handleSubmitSuccessNotification(payload) {
    const { offererId } = this.props.params
    const notificationMessageProps = {
      venueId: payload.id,
      offererId,
    }

    this.props.dispatch(
      showNotification({
        text: <NotificationMessage {...notificationMessageProps} />,
        type: 'success',
      })
    )
  }

  handleFormFail = formResolver => payload => {
    const errors = parseSubmitErrors(payload.errors)
    this.handleSubmitFailNotification(payload.errors)
    formResolver(errors)
  }

  handleFormSuccess = formResolver => payload => {
    const { history, params } = this.props
    const { offererId } = params
    this.handleSubmitSuccessNotification(payload)
    formResolver()

    const next = `/accueil?structure=${offererId}`
    history.push(next)
  }

  handleOnFormSubmit = formValues => {
    return new Promise(formResolver => {
      this.handleSubmitRequest({
        formValues,
        handleFail: this.handleFormFail(formResolver),
        handleSuccess: this.handleFormSuccess(formResolver),
      })
    })
  }

  onHandleRender = formProps => {
    const { history, params } = this.props
    const { offererId } = params
    const {
      isBankInformationWithSiretActive,
      venueTypes,
      venueLabels,
      offerer,
    } = this.state
    const readOnly = false
    const canSubmit = getCanSubmit(formProps)
    const { form, handleSubmit, values } = formProps
    const {
      isLocationFrozen: formIsLocationFrozen,
      latitude: formLatitude,
      longitude: formLongitude,
      siret: formSiret,
    } = values

    const siretValidOnCreation =
      !!formSiret && unhumanizeSiret(formSiret).length === 14
    return (
      <form name="venue" onSubmit={handleSubmit}>
        <IdentifierFields
          fieldReadOnlyBecauseFrozenFormSiret={siretValidOnCreation}
          formSiret={formSiret}
          isCreatedEntity
          readOnly={readOnly}
          venueLabels={venueLabels}
          venueTypes={venueTypes}
        />
        <WithdrawalDetailsFields isCreatedEntity readOnly={readOnly} />
        {isBankInformationWithSiretActive ? (
          <BusinessUnitFields isCreatingVenue offerer={offerer} />
        ) : (
          <BankInformation offerer={offerer} />
        )}
        <LocationFields
          fieldReadOnlyBecauseFrozenFormSiret={siretValidOnCreation}
          form={form}
          formIsLocationFrozen={formIsLocationFrozen}
          formLatitude={
            formLatitude === '' ? FRANCE_POSITION.latitude : formLatitude
          }
          formLongitude={
            formLongitude === '' ? FRANCE_POSITION.longitude : formLongitude
          }
          readOnly={readOnly}
        />
        <AccessibilityFields />
        <ContactInfosFields readOnly={false} />
        <hr />
        <div
          className="field is-grouped is-grouped-centered"
          style={{ justifyContent: 'space-between' }}
        >
          <ModifyOrCancelControl
            form={form}
            history={history}
            isCreatedEntity
            offererId={offererId}
            readOnly={readOnly}
          />

          <ReturnOrSubmitControl
            canSubmit={canSubmit}
            isCreatedEntity
            isRequestPending={formProps.submitting}
            offererId={offererId}
            readOnly={readOnly}
          />
        </div>
      </form>
    )
  }

  render() {
    const { location } = this.props
    const queryParams = new URLSearchParams(location.search)
    const { isReady } = this.state

    const decorators = [
      autoFillNoDisabilityCompliantDecorator,
      bindGetSuggestionsToLatitude,
      bindGetSuggestionsToLongitude,
    ]
    if (!this.state.isEntrepriseApiDisabled) {
      decorators.push(bindGetSiretInformationToSiret)
    }

    return (
      <div className="venue-page">
        <NavLink
          className="back-button has-text-primary"
          to={`/accueil?structure=${queryParams.get('offererId')}`}
        >
          <Icon svg="ico-back" />
          Accueil
        </NavLink>
        <PageTitle title="Créer un lieu" />
        <Titles title="Lieu" />
        <p className="advice">Ajoutez un lieu où accéder à vos offres.</p>

        {!isReady && <Spinner />}

        {isReady && (
          <Form
            decorators={decorators}
            initialValues={this.state.formInitialValues}
            name="venue"
            onSubmit={this.handleOnFormSubmit}
            render={this.onHandleRender}
          />
        )}
      </div>
    )
  }
}

VenueCreation.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  dispatch: PropTypes.func.isRequired,
  formInitialValues: PropTypes.shape().isRequired,
  history: PropTypes.shape().isRequired,
  isBankInformationWithSiretActive: PropTypes.bool.isRequired,
  isEntrepriseApiDisabled: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
  params: PropTypes.shape().isRequired,
}

export default withRouter(VenueCreation)
