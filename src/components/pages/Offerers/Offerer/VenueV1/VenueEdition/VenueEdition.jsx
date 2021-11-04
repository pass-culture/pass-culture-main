/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 * @debt deprecated "Gaël: deprecated usage of react-final-form"
 * @debt standard "Gaël: migration from classes components to function components"
 */

import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { Link, NavLink } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

import ModifyOrCancelControl from '../controls/ModifyOrCancelControl/ModifyOrCancelControl'
import ReturnOrSubmitControl from '../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'
import AccessibilityFields, {
  autoFillNoDisabilityCompliantDecorator,
} from '../fields/AccessibilityFields'
import BankInformation from '../fields/BankInformationFields/BankInformationFields'
import ContactInfosFields from '../fields/ContactInfosFields'
import IdentifierFields from '../fields/IdentifierFields/IdentifierFields'
import bindGetSuggestionsToLatitude from '../fields/LocationFields/decorators/bindGetSuggestionsToLatitude'
import bindGetSuggestionsToLongitude from '../fields/LocationFields/decorators/bindGetSuggestionsToLongitude'
import LocationFields from '../fields/LocationFields/LocationFields'
import { FRANCE_POSITION } from '../fields/LocationFields/utils/positions'
import WithdrawalDetailsFields from '../fields/WithdrawalDetailsFields/WithdrawalDetailsFields'
import VenueLabel from '../ValueObjects/VenueLabel'
import VenueType from '../ValueObjects/VenueType'

import VenueProvidersManager from './VenueProvidersManager'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel -> à faire lors de la V2 ?"
 */
class VenueEdition extends PureComponent {
  constructor() {
    super()
    this.state = { isRequestPending: false }
  }

  componentDidMount() {
    const { handleInitialRequest } = this.props
    handleInitialRequest()
  }

  handleFormFail = formResolver => (_state, action) => {
    const { handleSubmitRequestFail } = this.props
    const { payload } = action
    const nextState = { isRequestPending: false }
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitRequestFail(action)
    this.setState(nextState, () => formResolver(errors))
  }

  handleFormSuccess = (formResolver, hasDelayedUpdates) => (_state, action) => {
    const { venue, handleSubmitRequestSuccess, query, trackModifyVenue } = this.props

    const { id: venueId } = venue

    this.setState({ isRequestPending: false }, () => {
      handleSubmitRequestSuccess(action, { hasDelayedUpdates })
      formResolver()
    })

    trackModifyVenue(venueId)
    query.changeToReadOnly(null)
  }

  handleOnFormSubmit = formValues => {
    const { handleSubmitRequest } = this.props

    this.setState({ isRequestPending: true })
    const hasDelayedUpdates = [
      formValues.isAccessibilityAppliedOnAllOffers,
      formValues.isWithdrawalAppliedOnAllOffers,
      formValues.isEmailAppliedOnAllOffers,
    ].includes(true)

    return new Promise(resolve => {
      handleSubmitRequest({
        formValues,
        handleFail: this.handleFormFail(resolve),
        handleSuccess: this.handleFormSuccess(resolve, hasDelayedUpdates),
      })
    })
  }

  onHandleRender = formProps => {
    const {
      venue,
      history,
      match: {
        params: { offererId, venueId },
      },
      query,
      offerer,
      venueTypes,
      venueLabels,
      withdrawalDetailActive,
    } = this.props
    const { isRequestPending } = this.state
    const { readOnly } = query.context({
      id: venueId,
    })

    const { siret: initialSiret, withdrawalDetails: initialWithdrawalDetails } = venue || {}

    const canSubmit = getCanSubmit(formProps)

    const { form, handleSubmit, values } = formProps
    const {
      bookingEmail,
      isLocationFrozen: formIsLocationFrozen,
      latitude: formLatitude,
      longitude: formLongitude,
      siret: formSiret,
      venueTypeId,
      venueLabelId,
    } = values

    const isDirtyFieldBookingEmail = bookingEmail !== venue.bookingEmail
    const siretValidOnModification = initialSiret !== null
    const fieldReadOnlyBecauseFrozenFormSiret = !readOnly && siretValidOnModification

    return (
      <form
        data-testid="venue-edition-form"
        name="venue"
        onSubmit={handleSubmit}
      >
        <IdentifierFields
          fieldReadOnlyBecauseFrozenFormSiret={fieldReadOnlyBecauseFrozenFormSiret}
          formSiret={formSiret}
          initialSiret={initialSiret}
          isDirtyFieldBookingEmail={isDirtyFieldBookingEmail}
          readOnly={readOnly}
          venueLabelId={venueLabelId}
          venueLabels={venueLabels}
          venueTypeId={venueTypeId}
          venueTypes={venueTypes}
        />
        {withdrawalDetailActive && (
          <WithdrawalDetailsFields
            initialWithdrawalDetails={initialWithdrawalDetails}
            readOnly={readOnly}
          />
        )}
        <BankInformation
          offerer={offerer}
          venue={venue}
        />
        <LocationFields
          fieldReadOnlyBecauseFrozenFormSiret={fieldReadOnlyBecauseFrozenFormSiret}
          form={form}
          formIsLocationFrozen={formIsLocationFrozen}
          formLatitude={formLatitude === '' ? FRANCE_POSITION.latitude : formLatitude}
          formLongitude={formLongitude === '' ? FRANCE_POSITION.longitude : formLongitude}
          readOnly={readOnly}
        />
        <AccessibilityFields
          formValues={values}
          readOnly={readOnly}
          venue={venue}
        />
        <ContactInfosFields readOnly={readOnly} />
        <hr />
        <div
          className="field is-grouped is-grouped-centered"
          style={{ justifyContent: 'space-between' }}
        >
          <ModifyOrCancelControl
            form={form}
            history={history}
            offererId={offererId}
            readOnly={readOnly}
            venueId={venueId}
          />
          <ReturnOrSubmitControl
            canSubmit={canSubmit}
            isRequestPending={isRequestPending}
            offererId={offererId}
            readOnly={readOnly}
          />
        </div>
      </form>
    )
  }

  getInitialValues(venue) {
    let initialValues = { ...venue }
    const accessibilityFieldNames = [
      'audioDisabilityCompliant',
      'mentalDisabilityCompliant',
      'motorDisabilityCompliant',
      'visualDisabilityCompliant',
    ]
    accessibilityFieldNames.forEach(fieldName => {
      if (initialValues[fieldName] === null) {
        delete initialValues[fieldName]
      }
    })

    return initialValues
  }

  renderForm() {
    const { venue } = this.props
    const initialValues = this.getInitialValues(venue)
    const decorators = [
      autoFillNoDisabilityCompliantDecorator,
      bindGetSuggestionsToLatitude,
      bindGetSuggestionsToLongitude,
    ]

    return (
      <Form
        decorators={decorators}
        initialValues={initialValues}
        name="venue"
        onSubmit={this.handleOnFormSubmit}
        render={this.onHandleRender}
      />
    )
  }

  render() {
    const {
      venue,
      match: {
        params: { offererId, venueId },
      },
      offerer,
      query,
    } = this.props

    const { readOnly } = query.context({
      id: venueId,
    })

    const { id: initialId, isVirtual: initialIsVirtual, name: initialName } = venue || {}

    const pageTitle = readOnly ? 'Détails de votre lieu' : 'Modifier votre lieu'
    const actionLink = !!initialId && (
      <Link
        className="primary-button with-icon"
        to={`/offres/creation?lieu=${initialId}&structure=${offererId}`}
      >
        <AddOfferSvg />
        <span>
          Créer une offre
        </span>
      </Link>
    )

    return (
      <div className="venue-page">
        <NavLink
          className="back-button has-text-primary"
          to={`/accueil?structure=${offererId}`}
        >
          <Icon svg="ico-back" />
          Accueil
        </NavLink>
        <PageTitle title={pageTitle} />
        <Titles
          action={actionLink || undefined}
          subtitle={initialName}
          title="Lieu"
        />
        {!initialIsVirtual && (
          <>
            {venue && <VenueProvidersManager venue={venue} />}
            {venue && offerer && this.renderForm()}
          </>
        )}
      </div>
    )
  }
}

VenueEdition.defaultProps = {
  offerer: null,
  venue: null,
}

VenueEdition.propTypes = {
  handleInitialRequest: PropTypes.func.isRequired,
  handleSubmitRequest: PropTypes.func.isRequired,
  handleSubmitRequestFail: PropTypes.func.isRequired,
  handleSubmitRequestSuccess: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  offerer: PropTypes.shape(),
  query: PropTypes.shape().isRequired,
  trackModifyVenue: PropTypes.func.isRequired,
  venue: PropTypes.shape(),
  venueLabels: PropTypes.arrayOf(PropTypes.instanceOf(VenueLabel)).isRequired,
  venueTypes: PropTypes.arrayOf(PropTypes.instanceOf(VenueType)).isRequired,
  withdrawalDetailActive: PropTypes.bool.isRequired,
}

export default VenueEdition
