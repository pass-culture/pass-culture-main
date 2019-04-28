import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { NavLink } from 'react-router-dom'

import BankFieldsContainer from './BankFields/BankFieldsContainer'
import CreateOfferControl from './CreateOfferControl'
import { FRANCE_POSITION } from './GeoFields/positions'
import GeoFields from './GeoFields/GeoFields'
import IdentifierFields from './IdentifierFields/IdentifierFields'
import siretDecorator from './IdentifierFields/siretDecorator'
import ModifyOrCancelControl from './ModifyOrCancelControl/ModifyOrCancelControl'
import ReturnOrSubmitControl from './ReturnOrSubmitControl/ReturnOrSubmitControl'
import VenueProvidersManagerContainer from './VenueProvidersManager/VenueProvidersManagerContainer'
import HeroSection from 'components/layout/HeroSection'
import Icon from 'components/layout/Icon'
import Main from 'components/layout/Main'

const noop = () => {}

class Venue extends Component {
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
    } = this.props
    const { id: venueId } = formInitialValues
    const nextState = { isRequestPending: false }
    const { isCreatedEntity } = query.context({ id: venueId })

    this.setState(nextState, () => {
      handleSubmitRequestSuccess(state, action)
      if (isCreatedEntity) {
        history.push(`/structures/${offererId}`)
      } else {
        query.changeToReadOnly(null, { id: venueId })
      }

      formResolver()
    })
  }

  onFormSubmit = formValues => {
    const { handleSubmitRequest } = this.props

    this.setState({ isRequestPending: true })

    const formSubmitPromise = new Promise(resolve => {
      handleSubmitRequest({
        formValues,
        handleFail: this.handleFormFail(resolve),
        handleSuccess: this.handleFormSuccess(resolve),
      })
    })

    return formSubmitPromise
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
    const {
      iban: initialIban,
      id: initialId,
      isVirtual: initialIsVirtual,
      name: initialName,
      siret: initialSiret,
      thumbCount: initialThumbCount,
    } = formInitialValues || {}
    const { isCreatedEntity, isModifiedEntity, readOnly } = query.context({
      id: venueId,
    })
    const { isRequestPending } = this.state

    return (
      <Main
        backTo={this.buildBackToInfos(offererName, initialName, offererId)}
        name="venue"
        handleDataRequest={noop}>
        <HeroSection subtitle={initialName} title="Lieu">
          {isCreatedEntity && (
            <p className="subtitle">Ajoutez un lieu où accéder à vos offres.</p>
          )}

          {this.checkIfVenueExists(initialId) && !isCreatedEntity && (
            <NavLink
              to={`/offres/creation?lieu=${initialId}`}
              className="cta button is-primary">
              <span className="icon">
                <Icon svg="ico-offres-w" />
              </span>
              <span>Créer une offre</span>
            </NavLink>
          )}
        </HeroSection>

        {!isCreatedEntity && (
          <VenueProvidersManagerContainer venue={formInitialValues} />
        )}

        {!initialIsVirtual && (
          <Form
            decorators={[siretDecorator]}
            initialValues={formInitialValues}
            name="venue"
            onSubmit={this.onFormSubmit}
            render={formProps => {
              const canSubmit = getCanSubmit(formProps)
              const { form, handleSubmit, values } = formProps
              const {
                latitude: formLatitude,
                longitude: formLongitude,
                selectedAddress: formSelectedAddress,
                siret: formSiret,
              } = values

              const siretValidOnCreation = formSiret && formSiret.length === 14
              const fieldReadOnlyBecauseFrozenFormSiretOnCreation =
                isCreatedEntity && siretValidOnCreation

              const siretValidOnModification =
                typeof initialSiret !== 'undefined'
              const fieldReadOnlyBecauseFrozenFormSiretOnModification =
                isModifiedEntity && siretValidOnModification

              const fieldReadOnlyBecauseFrozenFormSiret =
                fieldReadOnlyBecauseFrozenFormSiretOnCreation ||
                fieldReadOnlyBecauseFrozenFormSiretOnModification

              return (
                <form onSubmit={handleSubmit}>
                  <IdentifierFields
                    fieldReadOnlyBecauseFrozenFormSiret={
                      fieldReadOnlyBecauseFrozenFormSiret
                    }
                    formSiret={formSiret}
                    initialSiret={initialSiret}
                    isCreatedEntity={isCreatedEntity}
                    isModifiedEntity={isModifiedEntity}
                    readOnly={readOnly}
                    withComment={
                      (isCreatedEntity && !siretValidOnCreation) ||
                      (isModifiedEntity && !siretValidOnModification)
                    }
                    withSiret={isCreatedEntity || initialSiret}
                  />
                  <BankFieldsContainer
                    initialIban={initialIban}
                    initialThumbCount={initialThumbCount}
                    readOnly={readOnly}
                  />
                  <GeoFields
                    fieldReadOnlyBecauseFrozenFormSiret={
                      fieldReadOnlyBecauseFrozenFormSiret
                    }
                    initialSiret={initialSiret}
                    form={form}
                    formLatitude={
                      formLatitude === ''
                        ? FRANCE_POSITION.latitude
                        : formLatitude
                    }
                    formLongitude={
                      formLongitude === ''
                        ? FRANCE_POSITION.longitude
                        : formLongitude
                    }
                    formSelectedAddress={formSelectedAddress}
                    formSiret={formSiret}
                    isModifiedEntity={isModifiedEntity}
                    readOnly={readOnly}
                  />
                  <hr />
                  <div
                    className="field is-grouped is-grouped-centered"
                    style={{ justifyContent: 'space-between' }}>
                    <ModifyOrCancelControl
                      isCreatedEntity={isCreatedEntity}
                      offererId={offererId}
                      venueId={venueId}
                      readOnly={readOnly}
                    />
                    {readOnly && <CreateOfferControl venueId={venueId} />}
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
            }}
          />
        )}
      </Main>
    )
  }
}

Venue.propTypes = {
  handleInitialRequest: PropTypes.func.isRequired,
  handleSubmitRequest: PropTypes.func.isRequired,
  handleSubmitRequestFail: PropTypes.func.isRequired,
  handleSubmitRequestSuccess: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  query: PropTypes.object.isRequired,
}

export default Venue
