import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { NavLink } from 'react-router-dom'
import Icon from '../../../layout/Icon'
import Main from '../../../layout/Main'
import Titles from '../../../layout/Titles/Titles'
import CreateControl from './../controls/CreateControl/CreateControl'
import ModifyOrCancelControl from './../controls/ModifyOrCancelControl/ModifyOrCancelControl'
import ReturnOrSubmitControl from './../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'
import BankFieldsContainer from './BankInformation/BankInformationLegacy/BankFieldsContainer'
import IdentifierFields from './../fields/IdentifierFields/IdentifierFields'
import bindGetSuggestionsToLatitude from './../fields/LocationFields/decorators/bindGetSuggestionsToLatitude'
import bindGetSuggestionsToLongitude from './../fields/LocationFields/decorators/bindGetSuggestionsToLongitude'
import LocationFields from './../fields/LocationFields/LocationFields'
import { FRANCE_POSITION } from './../fields/LocationFields/utils/positions'
import VenueProvidersManagerContainer from './VenueProvidersManager/VenueProvidersManagerContainer'
import RibsUploadFeatureFlip from '../../../layout/FeatureFlip/RibsUploadFeatureFlip'
import BankInformation from './BankInformation/BankInformation'
import VenueType from '../ValueObjects/VenueType'

const noop = () => {}

class VenueEdition extends PureComponent {
  constructor() {
    super()
    this.state = { isRequestPending: false }
  }

  componentDidMount() {
    const { handleInitialRequest } = this.props
    handleInitialRequest()
  }

  buildBackToInfos = (offererName, initialName, offererId) => {
    return {
      label: offererName === initialName ? 'STRUCTURE' : offererName,
      path: `/structures/${offererId}`,
    }
  }

  handleFormFail = formResolver => (_state, action) => {
    const { handleSubmitRequestFail } = this.props
    const { payload } = action
    const nextState = { isRequestPending: false }
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitRequestFail(action)
    this.setState(nextState, () => formResolver(errors))
  }

  handleFormSuccess = formResolver => (_state, action) => {
    const { venue, handleSubmitRequestSuccess, query, trackModifyVenue } = this.props

    const { id: venueId } = venue

    this.setState({ isRequestPending: false }, () => {
      handleSubmitRequestSuccess(action)
      formResolver()
    })

    trackModifyVenue(venueId)
    query.changeToReadOnly(null)
  }

  handleOnFormSubmit = formValues => {
    const { handleSubmitRequest } = this.props

    this.setState({ isRequestPending: true })

    return new Promise(resolve => {
      handleSubmitRequest({
        formValues,
        handleFail: this.handleFormFail(resolve),
        handleSuccess: this.handleFormSuccess(resolve),
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
    } = this.props
    const { isRequestPending } = this.state
    const { readOnly } = query.context({
      id: venueId,
    })

    const { bic, iban, siret: initialSiret } = venue || {}

    const canSubmit = getCanSubmit(formProps)
    const { form, handleSubmit, values } = formProps
    const {
      isLocationFrozen: formIsLocationFrozen,
      latitude: formLatitude,
      longitude: formLongitude,
      siret: formSiret,
    } = values

    const siretValidOnModification = initialSiret !== null
    const fieldReadOnlyBecauseFrozenFormSiret = !readOnly && siretValidOnModification
    const areBankInformationProvided = bic && iban

    return (
      <form
        name="venue"
        onSubmit={handleSubmit}
      >
        <IdentifierFields
          fieldReadOnlyBecauseFrozenFormSiret={fieldReadOnlyBecauseFrozenFormSiret}
          formSiret={formSiret}
          initialSiret={initialSiret}
          venueTypeId={formInitialValues.venueTypeId}
          venueTypes={venueTypes}
        />
        <BankFieldsContainer
          areBankInformationProvided={areBankInformationProvided}
          readOnly={readOnly}
        />
        <RibsUploadFeatureFlip
          legacy={
            <BankFieldsContainer
              areBankInformationProvided={areBankInformationProvided}
              readOnly={readOnly}
            />
          }
        >
          <BankInformation
            offerer={offerer}
            venue={venue}
          />
        </RibsUploadFeatureFlip>
        <LocationFields
          fieldReadOnlyBecauseFrozenFormSiret={fieldReadOnlyBecauseFrozenFormSiret}
          form={form}
          formIsLocationFrozen={formIsLocationFrozen}
          formLatitude={formLatitude === '' ? FRANCE_POSITION.latitude : formLatitude}
          formLongitude={formLongitude === '' ? FRANCE_POSITION.longitude : formLongitude}
          readOnly={readOnly}
        />
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
          {readOnly && <CreateControl
            offererId={offererId}
            venueId={venueId}
                       />}
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

  render() {
    const {
      venue,
      match: {
        params: { offererId },
      },
      offerer,
    } = this.props

    const { name: offererName } = offerer || {}
    const { id: initialId, isVirtual: initialIsVirtual, name: initialName } = venue || {}

    const decorators = [bindGetSuggestionsToLatitude, bindGetSuggestionsToLongitude]

    const showForm = !initialIsVirtual && typeof offerer !== 'undefined'

    const actionLink = !!initialId && (
      <NavLink
        className="cta button is-primary"
        id="action-create-offer"
        to={`/offres/creation?lieu=${initialId}&structure=${offererId}`}
      >
        <span className="icon">
          <Icon svg="ico-offres-w" />
        </span>
        <span>
          {'Créer une offre'}
        </span>
      </NavLink>
    )

    return (
      <Main
        backTo={this.buildBackToInfos(offererName, initialName, offererId)}
        handleDataRequest={noop}
        name="venue"
      >
        <Titles
          action={actionLink}
          subtitle={initialName}
          title="Lieu"
        />

        {venue && <VenueProvidersManagerContainer venue={venue} />}

        {showForm && (
          <Form
            decorators={decorators}
            initialValues={venue}
            name="venue"
            onSubmit={this.handleOnFormSubmit}
            render={this.onHandleRender}
          />
        )}
      </Main>
    )
  }
}

VenueEdition.propTypes = {
  handleInitialRequest: PropTypes.func.isRequired,
  handleSubmitRequest: PropTypes.func.isRequired,
  handleSubmitRequestFail: PropTypes.func.isRequired,
  handleSubmitRequestSuccess: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  offerer: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  trackModifyVenue: PropTypes.func.isRequired,
  venue: PropTypes.shape().isRequired,
  venueTypes: PropTypes.arrayOf(PropTypes.instanceOf(VenueType)).isRequired,
}

export default VenueEdition
