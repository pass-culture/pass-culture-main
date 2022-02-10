import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { NavLink } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
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

class VenueCreation extends PureComponent {
  constructor() {
    super()
    this.state = {
      isReady: false,
      offerer: null,
      venueTypes: null,
      venueLabels: null,
    }
  }

  componentDidMount() {
    const { handleInitialRequest } = this.props

    handleInitialRequest().then(({ offerer, venueTypes, venueLabels }) => {
      this.setState({
        isReady: true,
        offerer,
        venueTypes,
        venueLabels,
      })
    })
  }

  handleFormFail = formResolver => payload => {
    const { handleSubmitFailNotification } = this.props
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitFailNotification(payload.errors)
    formResolver(errors)
  }

  handleFormSuccess = formResolver => payload => {
    const {
      handleSubmitSuccessNotification,
      history,
      match: {
        params: { offererId },
      },
    } = this.props
    handleSubmitSuccessNotification(payload)
    formResolver()

    const next = `/accueil?structure=${offererId}`
    history.push(next)
  }

  handleOnFormSubmit = formValues => {
    const { handleSubmitRequest } = this.props
    return new Promise(formResolver => {
      handleSubmitRequest({
        formValues,
        handleFail: this.handleFormFail(formResolver),
        handleSuccess: this.handleFormSuccess(formResolver),
      })
    })
  }

  onHandleRender = formProps => {
    const {
      history,
      match: {
        params: { offererId },
      },
      isBankInformationWithSiretActive,
      isEntrepriseApiDisabled,
    } = this.props
    const { venueTypes, venueLabels, offerer } = this.state
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
      !!formSiret && formatSiret(formSiret).length === 14
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
    const {
      formInitialValues,
      match: {
        params: { offererId },
      },
      isEntrepriseApiDisabled,
    } = this.props
    const { isReady } = this.state

    const decorators = [
      autoFillNoDisabilityCompliantDecorator,
      bindGetSuggestionsToLatitude,
      bindGetSuggestionsToLongitude,
    ]
    if (!isEntrepriseApiDisabled) {
      decorators.push(bindGetSiretInformationToSiret)
    }

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

        {!isReady && <Spinner />}

        {isReady && (
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
  handleSubmitFailNotification: PropTypes.func.isRequired,
  handleSubmitRequest: PropTypes.func.isRequired,
  handleSubmitSuccessNotification: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  isBankInformationWithSiretActive: PropTypes.bool.isRequired,
  isEntrepriseApiDisabled: PropTypes.bool.isRequired,
  match: PropTypes.shape().isRequired,
}

export default VenueCreation
