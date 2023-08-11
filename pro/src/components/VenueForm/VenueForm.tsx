import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import {
  SharedCurrentUserResponseModel,
  VenueProviderResponse,
} from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { Offerer } from 'core/Offerers/types'
import { Providers, Venue } from 'core/Venue/types'
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
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import { VenueFormActionBar } from './VenueFormActionBar'
import { WithdrawalDetails } from './WithdrawalDetails'

import { VenueFormValues } from '.'

interface VenueFormProps {
  isCreatingVenue: boolean
  offerer: Offerer
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  venue?: Venue
  initialIsVirtual?: boolean
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
}: VenueFormProps) => {
  const {
    values: { isPermanent },
  } = useFormikContext<VenueFormValues>()
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
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
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */
          !!shouldDisplayImageVenueUploaderSection && (
            <ImageUploaderVenue isCreatingVenue={isCreatingVenue} />
          )
        }
        {!initialIsVirtual && (
          <FormLayout.Section
            title="Adresse du lieu"
            description="Cette adresse sera utilisée pour permettre aux jeunes de géolocaliser votre lieu."
          >
            <FormLayout.Row>
              <AddressSelect />
            </FormLayout.Row>
          </FormLayout.Section>
        )}
        <Activity
          venueTypes={venueTypes}
          venueLabels={venueLabels}
          isVenueVirtual={initialIsVirtual}
          isCreatingVenue={isCreatingVenue}
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
        {(canOffererCreateCollectiveOffer ||
          !!venue?.collectiveDmsApplication) &&
          ((isCreatingVenue && isSiretValued) || !isCreatingVenue) && (
            <CollectiveVenueInformations
              venue={venue}
              isCreatingVenue={isCreatingVenue}
              canCreateCollectiveOffer={canOffererCreateCollectiveOffer}
            />
          )}
        {((!isNewBankDetailsJourneyEnable && !isCreatingVenue) ||
          (isNewBankDetailsJourneyEnable && !venue?.siret)) &&
          venue && (
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
            offererId: offerer.id,
            user: user.currentUser,
          })}
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
