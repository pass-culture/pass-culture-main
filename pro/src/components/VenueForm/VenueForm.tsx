import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { VenueProviderResponse } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { IOfferer } from 'core/Offerers/types'
import { IProviders, IVenue } from 'core/Venue/types'
import {
  useNewOfferCreationJourney,
  useScrollToFirstErrorAfterSubmit,
} from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { venueSubmitRedirectUrl } from 'screens/VenueForm/utils/venueSubmitRedirectUrl'

import useCurrentUser from '../../hooks/useCurrentUser'
import RouteLeavingGuard, { BlockerFunction } from '../RouteLeavingGuard'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import { Address } from './Address'
import CollectiveVenueInformations from './CollectiveVenueInformations/CollectiveVenueInformations'
import { Contact } from './Contact'
import { EACInformation } from './EACInformation'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import { VenueFormActionBar } from './VenueFormActionBar'
import { WithdrawalDetails } from './WithdrawalDetails'

import { IVenueFormValues } from '.'

export interface IVenueForm {
  isCreatingVenue: boolean
  offerer: IOfferer
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: IProviders[]
  venueProvider?: VenueProviderResponse[]
  venue?: IVenue
  initialIsVirtual?: boolean
  isNewOnboardingActive: boolean
}

const VenueForm = ({
  isCreatingVenue,
  offerer,
  updateIsSiretValued,
  venueTypes,
  venueLabels,
  provider,
  venueProvider,
  venue,
  initialIsVirtual = false,
  isNewOnboardingActive,
}: IVenueForm) => {
  const {
    values: { isPermanent },
  } = useFormikContext<IVenueFormValues>()
  const shouldDisplayImageVenueUploaderSection = isPermanent
  useScrollToFirstErrorAfterSubmit()
  const location = useLocation()
  const user = useCurrentUser()

  const [canOffererCreateCollectiveOffer, setCanOffererCreateCollectiveOffer] =
    useState(false)
  const [isSiretValued, setIsSiretValued] = useState(true)

  useEffect(() => {
    canOffererCreateCollectiveOfferAdapter(offerer.id).then(response =>
      setCanOffererCreateCollectiveOffer(
        response.payload.isOffererEligibleToEducationalOffer
      )
    )
  }, [])

  const isNewOfferCreationJourney = useNewOfferCreationJourney()
  const isCollectiveDmsTrackingActive = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_DMS_TRACKING'
  )

  const shouldBlockNavigation: BlockerFunction = ({ nextLocation }) => {
    if (!isCreatingVenue) {
      return false
    }
    const url = venueSubmitRedirectUrl(
      isNewOfferCreationJourney,
      isCreatingVenue,
      offerer.id,
      venue?.id,
      user.currentUser
    )
    if (
      venue != null
        ? nextLocation.pathname + nextLocation.search === url
        : (nextLocation.pathname + nextLocation.search).startsWith(url)
    ) {
      return false
    } else {
      return true
    }
  }

  return (
    <div>
      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />
        {!isCreatingVenue &&
          !initialIsVirtual &&
          provider &&
          venueProvider &&
          venue && (
            <OffersSynchronization
              provider={provider}
              venueProvider={venueProvider}
              venue={venue}
            />
          )}
        <Informations
          isCreatedEntity={isCreatingVenue}
          readOnly={!isCreatingVenue}
          updateIsSiretValued={updateIsSiretValued}
          isVenueVirtual={initialIsVirtual}
          setIsSiretValued={setIsSiretValued}
          siren={offerer.siren}
          isNewOnboardingActive={isNewOnboardingActive}
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */
          !!shouldDisplayImageVenueUploaderSection && <ImageUploaderVenue />
        }
        {!initialIsVirtual && <Address />}
        <Activity
          venueTypes={venueTypes}
          venueLabels={venueLabels}
          isVenueVirtual={initialIsVirtual}
          isCreatingVenue={isCreatingVenue}
          isNewOfferCreationJourney={isNewOfferCreationJourney}
          isNewOnboardingActive={isNewOnboardingActive}
        />
        {!initialIsVirtual && (
          <>
            <Accessibility isCreatingVenue={isCreatingVenue} />
            {((isCreatingVenue && !isNewOfferCreationJourney) ||
              !isCreatingVenue) && (
              <WithdrawalDetails isCreatedEntity={isCreatingVenue} />
            )}
          </>
        )}
        <Contact
          isVenueVirtual={initialIsVirtual}
          isCreatingVenue={isCreatingVenue}
          isNewOfferCreationJourney={isNewOfferCreationJourney}
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */ canOffererCreateCollectiveOffer &&
            !isCollectiveDmsTrackingActive &&
            ((isCreatingVenue && isSiretValued) || !isCreatingVenue) && (
              <EACInformation isCreatingVenue={isCreatingVenue} venue={venue} />
            )
        }
        {
          /* istanbul ignore next: DEBT, TO FIX */
          isCollectiveDmsTrackingActive &&
            ((isCreatingVenue && isSiretValued) || !isCreatingVenue) && (
              <CollectiveVenueInformations
                venue={venue}
                isCreatingVenue={isCreatingVenue}
              />
            )
        }
        {!isCreatingVenue && venue && (
          <ReimbursementFields
            offerer={offerer}
            readOnly={false}
            scrollToSection={!!location.state || !!location.hash}
            venue={venue}
          />
        )}
        <RouteLeavingGuard
          shouldBlockNavigation={shouldBlockNavigation}
          dialogTitle="Voulez-vous quitter la création de lieu ?"
        >
          <p>Les informations non enregistrées seront perdues.</p>
        </RouteLeavingGuard>
        <VenueFormActionBar
          offererId={offerer.id}
          isCreatingVenue={isCreatingVenue}
        />
      </FormLayout>
    </div>
  )
}

export default VenueForm
