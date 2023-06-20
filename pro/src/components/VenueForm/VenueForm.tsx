import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import {
  SharedCurrentUserResponseModel,
  VenueProviderResponse,
} from 'apiClient/v1'
import { Address } from 'components/Address'
import FormLayout from 'components/FormLayout'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { IOfferer } from 'core/Offerers/types'
import { IProviders, IVenue } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { venueSubmitRedirectUrl } from 'screens/VenueForm/utils/venueSubmitRedirectUrl'

import useCurrentUser from '../../hooks/useCurrentUser'
import RouteLeavingGuard, { BlockerFunction } from '../RouteLeavingGuard'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import CollectiveVenueInformations from './CollectiveVenueInformations/CollectiveVenueInformations'
import { Contact } from './Contact'
import { EACInformation } from './EACInformation'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import { VenueFormActionBar } from './VenueFormActionBar'
import { WithdrawalDetails } from './WithdrawalDetails'

import { VenueFormValues } from '.'

interface VenueFormProps {
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

interface ShouldBlockVenueNavigationProps {
  isCreatingVenue: boolean
  offererId: number
  user: SharedCurrentUserResponseModel
}

type ShouldBlockVenueNavigation = (
  p: ShouldBlockVenueNavigationProps
) => BlockerFunction

export const shouldBlockVenueNavigation: ShouldBlockVenueNavigation =
  ({
    isCreatingVenue,
    offererId,
    user,
  }: ShouldBlockVenueNavigationProps): BlockerFunction =>
  ({ nextLocation }) => {
    if (!isCreatingVenue) {
      return false
    }

    const url = venueSubmitRedirectUrl(isCreatingVenue, offererId, user)
    const nextUrl = nextLocation.pathname + nextLocation.search

    return !nextUrl.startsWith(url)
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
}: VenueFormProps) => {
  const {
    values: { isPermanent },
  } = useFormikContext<VenueFormValues>()
  const shouldDisplayImageVenueUploaderSection = isPermanent
  useScrollToFirstErrorAfterSubmit()
  const location = useLocation()
  const user = useCurrentUser()

  const [canOffererCreateCollectiveOffer, setCanOffererCreateCollectiveOffer] =
    useState(false)
  const [isSiretValued, setIsSiretValued] = useState(true)

  useEffect(() => {
    canOffererCreateCollectiveOfferAdapter(offerer.nonHumanizedId).then(
      response =>
        setCanOffererCreateCollectiveOffer(
          response.payload.isOffererEligibleToEducationalOffer
        )
    )
  }, [])

  const isCollectiveDmsTrackingActive = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_DMS_TRACKING'
  )

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
        {!initialIsVirtual && (
          <FormLayout.Section
            title="Adresse du lieu"
            description="Cette adresse sera utilisée pour permettre aux jeunes de géolocaliser votre lieu."
          >
            <FormLayout.Row>
              <Address />
            </FormLayout.Row>
          </FormLayout.Section>
        )}
        <Activity
          venueTypes={venueTypes}
          venueLabels={venueLabels}
          isVenueVirtual={initialIsVirtual}
          isCreatingVenue={isCreatingVenue}
          isNewOnboardingActive={isNewOnboardingActive}
        />
        {!initialIsVirtual && (
          <>
            <Accessibility isCreatingVenue={isCreatingVenue} />
            {!isCreatingVenue && (
              <WithdrawalDetails isCreatedEntity={isCreatingVenue} />
            )}
          </>
        )}
        <Contact
          isVenueVirtual={initialIsVirtual}
          isCreatingVenue={isCreatingVenue}
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */ canOffererCreateCollectiveOffer &&
            !isCollectiveDmsTrackingActive &&
            ((isCreatingVenue && isSiretValued) || !isCreatingVenue) && (
              <EACInformation isCreatingVenue={isCreatingVenue} venue={venue} />
            )
        }
        {isCollectiveDmsTrackingActive &&
          (canOffererCreateCollectiveOffer ||
            !!venue?.collectiveDmsApplication) &&
          ((isCreatingVenue && isSiretValued) || !isCreatingVenue) && (
            <CollectiveVenueInformations
              venue={venue}
              isCreatingVenue={isCreatingVenue}
              canCreateCollectiveOffer={canOffererCreateCollectiveOffer}
            />
          )}
        {!isCreatingVenue && venue && (
          <ReimbursementFields
            offerer={offerer}
            readOnly={false}
            scrollToSection={!!location.state || !!location.hash}
            venue={venue}
          />
        )}
        <RouteLeavingGuard
          shouldBlockNavigation={shouldBlockVenueNavigation({
            isCreatingVenue,
            offererId: offerer.nonHumanizedId,
            user: user.currentUser,
          })}
          dialogTitle="Voulez-vous quitter la création de lieu ?"
        >
          <p>Les informations non enregistrées seront perdues.</p>
        </RouteLeavingGuard>
        <VenueFormActionBar
          offererId={offerer.nonHumanizedId}
          isCreatingVenue={isCreatingVenue}
        />
      </FormLayout>
    </div>
  )
}

export default VenueForm
