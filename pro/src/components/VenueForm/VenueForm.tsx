import { useFormikContext } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { VenueProviderResponse } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { IOfferer } from 'core/Offerers/types'
import { IProviders, IVenue } from 'core/Venue/types'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import ReimbursementFields from 'pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { venueSubmitRedirectUrl } from 'screens/VenueForm/utils/venueSubmitRedirectUrl'

import useActiveFeature from '../../hooks/useActiveFeature'
import useCurrentUser from '../../hooks/useCurrentUser'
import RouteLeavingGuard, {
  IShouldBlockNavigationReturnValue,
} from '../RouteLeavingGuard'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import { Address } from './Address'
import { Contact } from './Contact'
import { EACInformation } from './EACInformation'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { OffersSynchronization } from './OffersSynchronization'
import { VenueFormActionBar } from './VenueFormActionBar'
import { WithdrawalDetails } from './WithdrawalDetails'

import { IVenueFormValues } from '.'

interface IVenueForm {
  isCreatingVenue: boolean
  offerer: IOfferer
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: IProviders[]
  venueProvider?: VenueProviderResponse[]
  venue?: IVenue
  initialIsVirtual?: boolean
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

  const isNewOfferCreationJourney = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'
  )

  const shouldBlockNavigation = useCallback(
    (nextLocation: Location): IShouldBlockNavigationReturnValue => {
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
          : nextLocation.pathname.startsWith(url)
      ) {
        return {
          shouldBlock: false,
        }
      } else {
        return { shouldBlock: true }
      }
    },
    [location]
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
            ((isCreatingVenue && isSiretValued) || !isCreatingVenue) && (
              <EACInformation isCreatingVenue={isCreatingVenue} venue={venue} />
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
          when={isCreatingVenue}
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
