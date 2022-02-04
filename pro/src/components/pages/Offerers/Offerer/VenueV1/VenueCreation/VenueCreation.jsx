import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { NavLink } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'

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
import { formatSiret } from '../siret/formatSiret'
import VenueLabel from '../ValueObjects/VenueLabel'
import VenueType from '../ValueObjects/VenueType'

class VenueCreation extends PureComponent {
  constructor() {
    super()
    this.state = { isRequestPending: false }
  }

  componentDidMount() {
    const { handleInitialRequest } = this.props
    handleInitialRequest()
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
      handleSubmitRequestSuccess,
      history,
      match: {
        params: { offererId },
      },
    } = this.props

    const nextState = { isRequestPending: false }

    this.setState(nextState, () => {
      handleSubmitRequestSuccess(state, action)
      formResolver()
    })

    const next = `/accueil?structure=${offererId}`
    history.push(next)
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
      history,
      match: {
        params: { offererId, venueId },
      },
      venueTypes,
      venueLabels,
      offerer,
      isBankInformationWithSiretActive,
      isEntrepriseApiDisabled,
    } = this.props
    const { isRequestPending } = this.state
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
      formSiret && formatSiret(formSiret).length === 14
    return (
      <form name="venue" onSubmit={handleSubmit}>
        <IdentifierFields
          fieldReadOnlyBecauseFrozenFormSiret={siretValidOnCreation}
          formSiret={formSiret}
          isCreatedEntity
          isEntrepriseApiDisabled={isEntrepriseApiDisabled}
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
        <ContactInfosFields />
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
            venueId={venueId}
          />
          <ReturnOrSubmitControl
            canSubmit={canSubmit}
            isCreatedEntity
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
        params: { offererId },
      },
      offerer,
      isEntrepriseApiDisabled,
    } = this.props

    const decorators = [
      autoFillNoDisabilityCompliantDecorator,
      bindGetSuggestionsToLatitude,
      bindGetSuggestionsToLongitude,
    ]
    if (!isEntrepriseApiDisabled) {
      decorators.push(bindGetSiretInformationToSiret)
    }

    const showForm = typeof offerer !== 'undefined'

    return (
      <div className="venue-page">
        <NavLink
          className="back-button has-text-primary"
          to={`/accueil?structure=${offererId}`}
        >
          <Icon svg="ico-back" />
          Accueil
        </NavLink>
        <PageTitle title="Créer un lieu" />
        <Titles title="Lieu" />
        <p className="advice">Ajoutez un lieu où accéder à vos offres.</p>

        {showForm && (
          <Form
            decorators={decorators}
            initialValues={formInitialValues}
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
  formInitialValues: PropTypes.shape().isRequired,
  handleInitialRequest: PropTypes.func.isRequired,
  handleSubmitRequest: PropTypes.func.isRequired,
  handleSubmitRequestFail: PropTypes.func.isRequired,
  handleSubmitRequestSuccess: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  isBankInformationWithSiretActive: PropTypes.bool.isRequired,
  isEntrepriseApiDisabled: PropTypes.bool.isRequired,
  match: PropTypes.shape().isRequired,
  offerer: PropTypes.shape().isRequired,
  venueLabels: PropTypes.arrayOf(PropTypes.instanceOf(VenueLabel)).isRequired,
  venueTypes: PropTypes.arrayOf(PropTypes.instanceOf(VenueType)).isRequired,
}

export default VenueCreation
