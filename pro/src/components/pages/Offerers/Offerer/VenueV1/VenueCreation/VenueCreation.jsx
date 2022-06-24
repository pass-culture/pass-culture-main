import AccessibilityFields, {
  autoFillNoDisabilityCompliantDecorator,
} from '../fields/AccessibilityFields'
import IdentifierFields, {
  bindGetSiretInformationToSiret,
} from '../fields/IdentifierFields'
import LocationFields, {
  FRANCE_POSITION,
  bindGetSuggestionsToLatitude,
  bindGetSuggestionsToLongitude,
} from '../fields/LocationFields'
import { NavLink, useHistory, useParams } from 'react-router-dom'
import React, { useEffect, useState } from 'react'

import {
  createVenue,
  getOfferer,
  getVenueLabels,
  getVenueTypes,
} from 'repository/pcapi/pcapi'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'

import BankInformation from '../fields/BankInformationFields'
import BusinessUnitFields from '../fields/BankInformationFields/BusinessUnitFields'
import ContactInfosFields from '../fields/ContactInfosFields'
import { Form } from 'react-final-form'
import Icon from 'components/layout/Icon'
import ModifyOrCancelControl from '../controls/ModifyOrCancelControl/ModifyOrCancelControl'
import NotificationMessage from '../Notification'
import PageTitle from 'components/layout/PageTitle/PageTitle'
/*eslint no-undef: 0*/
import ReturnOrSubmitControl from '../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import VenueType from '../ValueObjects/VenueType'
import WithdrawalDetailsFields from '../fields/WithdrawalDetailsFields'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import { sortByLabel } from 'utils/strings'
import { unhumanizeSiret } from 'core/Venue/utils'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'

const VenueCreation = () => {
  const [isReady, setIsReady] = useState(false)
  const [offerer, setOfferer] = useState(null)

  const [venueTypes, setVenueTypes] = useState(null)
  const [venueLabels, setVenueLabels] = useState(null)
  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  const isEntrepriseApiDisabled = useActiveFeature('DISABLE_ENTERPRISE_API')
  const isNewBankInformationCreation = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )
  const { offererId } = useParams()
  const history = useHistory()
  const notify = useNotification()
  const { currentUser } = useCurrentUser()

  const formInitialValues = {
    managingOffererId: offererId,
    bookingEmail: currentUser.email,
  }

  useEffect(() => {
    const handleInitialRequest = async () => {
      const offererRequest = getOfferer(offererId)
      const venueTypesRequest = getVenueTypes().then(venueTypes => {
        return venueTypes.map(type => new VenueType(type))
      })
      const venueLabelsRequest = getVenueLabels().then(labels =>
        sortByLabel(labels)
      )
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
    handleInitialRequest().then(({ offerer, venueTypes, venueLabels }) => {
      setOfferer(offerer)
      setVenueTypes(venueTypes)
      setVenueLabels(venueLabels)
      setIsReady(true)
    })
  }, [offererId])

  const handleSubmitRequest = async ({
    formValues,
    handleFail,
    handleSuccess,
  }) => {
    const body = formatVenuePayload(formValues, true)
    try {
      const response = await createVenue(body)
      handleSuccess(response)
    } catch (responseError) {
      handleFail(responseError)
    }
  }
  const handleSubmitFailNotification = errors => {
    let text = 'Une ou plusieurs erreurs sont présentes dans le formulaire.'
    if (errors.global) {
      text = `${text} ${errors.global[0]}`
    }

    notify.error(text)
  }

  const handleSubmitSuccessNotification = payload => {
    const notificationMessageProps = {
      venueId: payload.id,
      offererId,
    }
    notify.success(<NotificationMessage {...notificationMessageProps} />)
  }

  const handleFormFail = formResolver => payload => {
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitFailNotification(payload.errors)
    formResolver(errors)
  }

  const handleFormSuccess = formResolver => payload => {
    handleSubmitSuccessNotification(payload)
    formResolver()
    const next = isNewBankInformationCreation
      ? `/structures/${offererId}/lieux/${payload.id}?modification`
      : `/accueil?structure=${offererId}`
    history.push(next, isNewBankInformationCreation)
  }

  const handleOnFormSubmit = formValues => {
    return new Promise(formResolver => {
      handleSubmitRequest({
        formValues,
        handleFail: handleFormFail(formResolver),
        handleSuccess: handleFormSuccess(formResolver),
      })
    })
  }

  const onHandleRender = formProps => {
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
          siren={offerer.siren}
          venueLabels={venueLabels}
          venueTypes={venueTypes}
        />
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
          isAddressRequired={true}
        />
        <AccessibilityFields />
        <WithdrawalDetailsFields isCreatedEntity readOnly={readOnly} />
        <ContactInfosFields readOnly={false} />
        {!isNewBankInformationCreation &&
          (isBankInformationWithSiretActive ? (
            <BusinessUnitFields isCreatingVenue offerer={offerer} />
          ) : (
            <BankInformation offerer={offerer} />
          ))}
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
            isNewBankInformationCreation={isNewBankInformationCreation}
            isRequestPending={formProps.submitting}
            offererId={offererId}
            readOnly={readOnly}
          />
        </div>
      </form>
    )
  }

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
          name="venue"
          initialValues={formInitialValues}
          onSubmit={handleOnFormSubmit}
          render={onHandleRender}
        />
      )}
    </div>
  )
}
export default VenueCreation
