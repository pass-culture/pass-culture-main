import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors, removeWhitespaces } from 'react-final-form-utils'
import { NavLink } from 'react-router-dom'
import Icon from '../../../layout/Icon'
import Main from '../../../layout/Main'
import Titles from '../../../layout/Titles/Titles'
import CreateControl from './../controls/CreateControl/CreateControl'
import ModifyOrCancelControl from './../controls/ModifyOrCancelControl/ModifyOrCancelControl'
import ReturnOrSubmitControl from './../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'

import BankFieldsContainer from './../fields/BankFields/BankFieldsContainer'
import bindGetSiretInformationToSiret from './../fields/IdentifierFields/decorators/bindGetSiretInformationToSiret'
import IdentifierFields from './../fields/IdentifierFields/IdentifierFields'
import bindGetSuggestionsToLatitude from './../fields/LocationFields/decorators/bindGetSuggestionsToLatitude'
import bindGetSuggestionsToLongitude from './../fields/LocationFields/decorators/bindGetSuggestionsToLongitude'
import LocationFields from './../fields/LocationFields/LocationFields'
import { FRANCE_POSITION } from './../fields/LocationFields/utils/positions'
import VenueProvidersManagerContainer from './../VenueProvidersManager/VenueProvidersManagerContainer'

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

  checkIfVenueExists = initialVenueId => {
    return !!initialVenueId
  }

  handleFormFail = formResolver => (state, action) => {
    const { handleSubmitRequestFail } = this.props
    const { payload } = action
    const nextState = { isRequestPending: false }
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitRequestFail(state, action)
    this.setState(nextState, () => formResolver(errors))
  }

  handleFormSuccess = formResolver => (state, action) => {
    const {
      formInitialValues,
      handleSubmitRequestSuccess,
      history,
      match: {
        params: { offererId },
      },
      query,
      trackCreateVenue,
      trackModifyVenue,
    } = this.props

    const { id: venueId } = formInitialValues
    const nextState = { isRequestPending: false }
    const { isCreatedEntity } = query.context()

    this.setState(nextState, () => {
      handleSubmitRequestSuccess(state, action)
      formResolver()
    })

    const createdVenueId = action.payload.datum.id

    if (isCreatedEntity) {
      history.push(`/structures/${offererId}`)
      trackCreateVenue(createdVenueId)
    } else {
      trackModifyVenue(venueId)
      query.changeToReadOnly(null)
    }
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
      formInitialValues,
      history,
      match: {
        params: { offererId, venueId },
      },
      query,
    } = this.props
    const { isRequestPending } = this.state
    const { isCreatedEntity, isModifiedEntity, readOnly } = query.context({
      id: venueId,
    })

    const { bic, iban, siret: initialSiret } = formInitialValues || {}

    const canSubmit = getCanSubmit(formProps)
    const { form, handleSubmit, values } = formProps
    const {
      isLocationFrozen: formIsLocationFrozen,
      latitude: formLatitude,
      longitude: formLongitude,
      siret: formSiret,
    } = values

    const siretValidOnCreation = formSiret && removeWhitespaces(formSiret).length === 14
    const fieldReadOnlyBecauseFrozenFormSiretOnCreation = isCreatedEntity && siretValidOnCreation

    const siretValidOnModification = initialSiret !== null

    const fieldReadOnlyBecauseFrozenFormSiretOnModification =
      isModifiedEntity && siretValidOnModification

    const fieldReadOnlyBecauseFrozenFormSiret =
      fieldReadOnlyBecauseFrozenFormSiretOnCreation ||
      fieldReadOnlyBecauseFrozenFormSiretOnModification

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
          isCreatedEntity={isCreatedEntity}
          isModifiedEntity={isModifiedEntity}
          readOnly={readOnly}
        />
        <BankFieldsContainer
          areBankInformationProvided={areBankInformationProvided}
          readOnly={readOnly}
        />
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
            isCreatedEntity={isCreatedEntity}
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
            isCreatedEntity={isCreatedEntity}
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
      formInitialValues,
      match: {
        params: { offererId, venueId },
      },
      query,
      offerer,
    } = this.props

    const { name: offererName } = offerer || {}
    const { id: initialId, isVirtual: initialIsVirtual, name: initialName } =
      formInitialValues || {}
    const { isCreatedEntity } = query.context({
      id: venueId,
    })

    const decorators = [bindGetSuggestionsToLatitude, bindGetSuggestionsToLongitude]

    if (isCreatedEntity) {
      decorators.push(bindGetSiretInformationToSiret)
    }

    const showForm = !initialIsVirtual && typeof offerer !== 'undefined'

    const isDiplayedOrModifiedVenue = this.checkIfVenueExists(initialId) && !isCreatedEntity

    const actionLink = isDiplayedOrModifiedVenue && (
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
        {isCreatedEntity && <p className="advice">
          {'Ajoutez un lieu où accéder à vos offres.'}
                            </p>}

        {!isCreatedEntity && <VenueProvidersManagerContainer venue={formInitialValues} />}

        {showForm && (
          <Form
            decorators={decorators}
            initialValues={formInitialValues}
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
  formInitialValues: PropTypes.shape().isRequired,
  handleInitialRequest: PropTypes.func.isRequired,
  handleSubmitRequest: PropTypes.func.isRequired,
  handleSubmitRequestFail: PropTypes.func.isRequired,
  handleSubmitRequestSuccess: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  offerer: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  trackCreateVenue: PropTypes.func.isRequired,
  trackModifyVenue: PropTypes.func.isRequired,
}

export default VenueEdition
