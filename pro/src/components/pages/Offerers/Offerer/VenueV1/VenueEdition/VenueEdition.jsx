import PropTypes from 'prop-types'
import React, { useEffect, useRef, useState } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { Link, NavLink } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import { Banner } from 'ui-kit'

import ModifyOrCancelControl from '../controls/ModifyOrCancelControl/ModifyOrCancelControl'
import ReturnOrSubmitControl from '../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'
import AccessibilityFields, {
  autoFillNoDisabilityCompliantDecorator,
} from '../fields/AccessibilityFields'
import BankInformation from '../fields/BankInformationFields/BankInformationFields'
import BusinessUnitFields from '../fields/BankInformationFields/BusinessUnitFields'
import ContactInfosFields from '../fields/ContactInfosFields'
import IdentifierFields from '../fields/IdentifierFields/IdentifierFields'
import bindGetSuggestionsToLatitude from '../fields/LocationFields/decorators/bindGetSuggestionsToLatitude'
import bindGetSuggestionsToLongitude from '../fields/LocationFields/decorators/bindGetSuggestionsToLongitude'
import LocationFields from '../fields/LocationFields/LocationFields'
import { FRANCE_POSITION } from '../fields/LocationFields/utils/positions'
import WithdrawalDetailsFields from '../fields/WithdrawalDetailsFields/WithdrawalDetailsFields'
import VenueLabel from '../ValueObjects/VenueLabel'
import VenueType from '../ValueObjects/VenueType'

import DeleteBusinessUnitConfirmationDialog from './DeleteBusinessUnitConfirmationDialog/DeleteBusinessUnitConfirmationDialog'
import { DisplayVenueInAppLink } from './DisplayVenueInAppLink'
import { ImageVenueUploaderSection } from './ImageVenueUploaderSection/ImageVenueUploaderSection'
import VenueProvidersManager from './VenueProvidersManager'

const VenueEdition = ({
  handleInitialRequest,
  handleSubmitRequest,
  handleSubmitRequestFail,
  handleSubmitRequestSuccess,
  history,
  match: {
    params: { offererId, venueId },
  },
  offerer,
  query,
  venue,
  venueLabels,
  venueTypes,
}) => {
  const [isRequestPending, setIsRequestPending] = useState(false)
  const [showConfirmationDialog, setShowConfirmationDialog] = useState(false)
  const deleteBusinessUnitConfirmed = useRef(false)

  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )

  const shouldDisplayImageVenueUploaderSection =
    useActiveFeature('PRO_ENABLE_UPLOAD_VENUE_IMAGE') && venue?.isPermanent

  // TODO check that it's execute only once when initialize
  useEffect(() => handleInitialRequest(), [handleInitialRequest])

  const pageNotFoundRedirect = () => history.push('/404')

  const onConfirmDeleteBusinessUnit = submit => {
    deleteBusinessUnitConfirmed.current = true
    setShowConfirmationDialog(false)
    submit()
  }

  const handleFormFail = formResolver => (_state, action) => {
    const { payload } = action
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitRequestFail(action)
    formResolver(errors)
    setIsRequestPending(false)
  }

  const handleFormSuccess =
    (formResolver, hasDelayedUpdates) => (_state, action) => {
      handleSubmitRequestSuccess(action, { hasDelayedUpdates })
      formResolver()
      query.changeToReadOnly(null)
      setIsRequestPending(false)
    }

  const handleOnFormSubmit = formValues => {
    if (
      !deleteBusinessUnitConfirmed.current &&
      venue.isBusinessUnitMainVenue &&
      formValues.businessUnitId != venue.businessUnitId
    ) {
      setShowConfirmationDialog(true)
      return
    }
    deleteBusinessUnitConfirmed.current = false
    setIsRequestPending(true)
    const hasDelayedUpdates = [
      formValues.isAccessibilityAppliedOnAllOffers,
      formValues.isWithdrawalAppliedOnAllOffers,
      formValues.isEmailAppliedOnAllOffers,
    ].includes(true)

    return new Promise(resolve => {
      handleSubmitRequest({
        formValues,
        handleFail: handleFormFail(resolve),
        handleSuccess: handleFormSuccess(resolve, hasDelayedUpdates),
      })
    })
  }

  const onHandleRender = formProps => {
    const { readOnly } = query.context({
      id: venueId,
    })
    const {
      siret: initialSiret,
      isVirtual: initialIsVirtual,
      withdrawalDetails: initialWithdrawalDetails,
    } = venue || {}
    const canSubmit = getCanSubmit(formProps)
    const { form, handleSubmit, values } = formProps

    const {
      bookingEmail,
      isLocationFrozen: formIsLocationFrozen,
      latitude: formLatitude,
      longitude: formLongitude,
      siret: formSiret,
      venueTypeCode,
      venueLabelId,
    } = values

    const cancelBusinessUnitModification = form => {
      form.change('businessUnitId', venue.businessUnitId)
      setShowConfirmationDialog(false)
    }

    const isDirtyFieldBookingEmail = bookingEmail !== venue.bookingEmail
    const siretValidOnModification = initialSiret !== null
    const fieldReadOnlyBecauseFrozenFormSiret =
      !readOnly && siretValidOnModification

    return (
      <>
        <form
          data-testid="venue-edition-form"
          name="venue"
          onSubmit={handleSubmit}
        >
          <IdentifierFields
            fieldReadOnlyBecauseFrozenFormSiret={
              fieldReadOnlyBecauseFrozenFormSiret
            }
            formSiret={formSiret}
            initialSiret={initialSiret}
            isDirtyFieldBookingEmail={isDirtyFieldBookingEmail}
            readOnly={readOnly || initialIsVirtual}
            venueIsVirtual={initialIsVirtual}
            venueLabelId={venueLabelId}
            venueLabels={venueLabels}
            venueTypeCode={venueTypeCode}
            venueTypes={venueTypes}
          />
          {!initialIsVirtual && (
            <WithdrawalDetailsFields
              initialWithdrawalDetails={initialWithdrawalDetails}
              readOnly={readOnly}
            />
          )}
          {!!shouldDisplayImageVenueUploaderSection && (
            <ImageVenueUploaderSection
              venueId={venue.id}
              venueImage={venue.bannerUrl}
            />
          )}
          {isBankInformationWithSiretActive ? (
            // FIXME
            // the first response on offerers do not return  venue.BusinessUnit
            // the second on venues does
            venue.businessUnit !== undefined && (
              <BusinessUnitFields
                offerer={offerer}
                readOnly={readOnly}
                venue={venue}
              />
            )
          ) : (
            <BankInformation offerer={offerer} venue={venue} />
          )}
          {!initialIsVirtual && (
            <>
              <LocationFields
                fieldReadOnlyBecauseFrozenFormSiret={
                  fieldReadOnlyBecauseFrozenFormSiret
                }
                form={form}
                formIsLocationFrozen={formIsLocationFrozen}
                formLatitude={
                  formLatitude === '' ? FRANCE_POSITION.latitude : formLatitude
                }
                formLongitude={
                  formLongitude === ''
                    ? FRANCE_POSITION.longitude
                    : formLongitude
                }
                readOnly={readOnly}
              />
              <AccessibilityFields
                formValues={values}
                readOnly={readOnly}
                venue={venue}
              />
              <ContactInfosFields readOnly={readOnly} />
            </>
          )}
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
        {showConfirmationDialog && (
          <DeleteBusinessUnitConfirmationDialog
            onCancel={() => cancelBusinessUnitModification(form)}
            onConfirm={() => onConfirmDeleteBusinessUnit(handleSubmit)}
          />
        )}
      </>
    )
  }

  const getVirtualVenueName = () => `${offerer.name} (Offre numérique)`

  const getInitialValues = venue => {
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

    if (initialValues.isVirtual) {
      initialValues.name = getVirtualVenueName()
    }

    return initialValues
  }

  const renderForm = () => {
    const initialValues = getInitialValues(venue)
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
        onSubmit={handleOnFormSubmit}
        render={formProps => {
          return onHandleRender(formProps)
        }}
      />
    )
  }

  const { readOnly } = query.context({
    id: venueId,
  })

  const {
    id: initialId,
    isVirtual: initialIsVirtual,
    name: initialName,
  } = venue || {}

  const pageTitle = readOnly ? 'Détails de votre lieu' : 'Modifier votre lieu'

  const actionLink = !!initialId && (
    <Link
      className="primary-button with-icon"
      to={`/offre/creation?lieu=${initialId}&structure=${offererId}`}
    >
      <AddOfferSvg />
      <span>Créer une offre</span>
    </Link>
  )

  if (initialIsVirtual && !isBankInformationWithSiretActive) {
    pageNotFoundRedirect()
    return null
  }

  const pageSubtitle = initialIsVirtual ? getVirtualVenueName() : initialName

  if (!venue) return null

  return (
    <div className="venue-page">
      <NavLink
        className="back-button has-text-primary"
        to={`/accueil?structure=${offererId}`}
      >
        <Icon svg="ico-back" />
        Accueil
      </NavLink>
      {venue.isPermanent && (
        <DisplayVenueInAppLink
          className="venue-page-view-venue-cta"
          nonHumanizedId={venue.nonHumanizedId}
        />
      )}
      {venue.businessUnit && !venue.businessUnit.siret && (
        <Banner
          className="banner-invalid-bu"
          href={`/structures/${offererId}/point-de-remboursement/`}
          icon="ico-right-circle-arrow"
          linkTitle="Rattacher votre lieu à un point de remboursement valide"
        >
          Ce lieu n’est pas rattaché à un point de remboursement valide. Pour
          continuer à percevoir vos remboursements, veuillez renseigner un SIRET
          de référence pour votre point de remboursement.
        </Banner>
      )}
      <PageTitle title={pageTitle} />
      <Titles
        action={actionLink || undefined}
        subtitle={pageSubtitle}
        title="Lieu"
      />
      {venue && !initialIsVirtual && <VenueProvidersManager venue={venue} />}
      {venue && offerer && renderForm()}
    </div>
  )
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
  venue: PropTypes.shape(),
  venueLabels: PropTypes.arrayOf(PropTypes.instanceOf(VenueLabel)).isRequired,
  venueTypes: PropTypes.arrayOf(PropTypes.instanceOf(VenueType)).isRequired,
}

export default VenueEdition
