import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import {
  SharedCurrentUserResponseModel,
  VenueProviderResponse,
} from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { Offerer } from 'core/Offerers/types'
import { Providers } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import { venueSubmitRedirectUrl } from 'screens/VenueForm/utils/venueSubmitRedirectUrl'

import useCurrentUser from '../../hooks/useCurrentUser'
import RouteLeavingGuard, { BlockerFunction } from '../RouteLeavingGuard'

import { Accessibility } from './Accessibility'
import { Activity } from './Activity'
import { Contact } from './Contact'
import { EACInformation } from './EACInformation/EACInformation'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import { Informations } from './Informations'
import { VenueFormActionBar } from './VenueFormActionBar'

import { VenueFormValues } from '.'

interface VenueFormProps {
  offerer: Offerer
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  initialIsVirtual?: boolean
}

interface ShouldBlockVenueNavigationProps {
  offererId: number
  user: SharedCurrentUserResponseModel
}

type ShouldBlockVenueNavigation = (
  p: ShouldBlockVenueNavigationProps
) => BlockerFunction

export const shouldBlockVenueNavigation: ShouldBlockVenueNavigation =
  ({ offererId, user }: ShouldBlockVenueNavigationProps): BlockerFunction =>
  ({ nextLocation }) => {
    const url = venueSubmitRedirectUrl(true, offererId, user)
    const nextUrl = nextLocation.pathname + nextLocation.search

    return !nextUrl.startsWith(url)
  }

export const VenueCreationForm = ({
  offerer,
  updateIsSiretValued,
  venueTypes,
  venueLabels,
  initialIsVirtual = false,
}: VenueFormProps) => {
  const {
    values: { isPermanent },
  } = useFormikContext<VenueFormValues>()
  const shouldDisplayImageVenueUploaderSection = isPermanent
  useScrollToFirstErrorAfterSubmit()
  const user = useCurrentUser()

  const [canOffererCreateCollectiveOffer, setCanOffererCreateCollectiveOffer] =
    useState(false)
  const [isSiretValued, setIsSiretValued] = useState(true)

  useEffect(() => {
    const loadCanOffererCreateCollectiveOffer = async () => {
      const response = await canOffererCreateCollectiveOfferAdapter(offerer.id)
      setCanOffererCreateCollectiveOffer(
        response.payload.isOffererEligibleToEducationalOffer
      )
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadCanOffererCreateCollectiveOffer()
  }, [offerer.id])

  return (
    <div>
      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />

        <Informations
          isCreatedEntity={true}
          readOnly={false}
          updateIsSiretValued={updateIsSiretValued}
          isVenueVirtual={initialIsVirtual}
          setIsSiretValued={setIsSiretValued}
          siren={offerer.siren}
        />
        {
          /* istanbul ignore next: DEBT, TO FIX */
          !!shouldDisplayImageVenueUploaderSection && (
            <ImageUploaderVenue isCreatingVenue={true} />
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
          isCreatingVenue={true}
        />

        {!initialIsVirtual && <Accessibility isCreatingVenue={true} />}

        <Contact isVenueVirtual={initialIsVirtual} isCreatingVenue={true} />

        {canOffererCreateCollectiveOffer && isSiretValued && (
          <FormLayout.Section
            title="Mes informations pour les enseignants"
            id="venue-collective-data"
            description={
              canOffererCreateCollectiveOffer
                ? ''
                : 'Pour publier des offres à destination des scolaires, votre lieu doit être référencé sur ADAGE, la plateforme dédiée aux enseignants et aux chefs d’établissements.'
            }
          >
            <EACInformation />
          </FormLayout.Section>
        )}

        <RouteLeavingGuard
          shouldBlockNavigation={shouldBlockVenueNavigation({
            offererId: offerer.id,
            user: user.currentUser,
          })}
          dialogTitle="Voulez-vous quitter la création de lieu ?"
        >
          <p>Les informations non enregistrées seront perdues.</p>
        </RouteLeavingGuard>

        <VenueFormActionBar isCreatingVenue={true} />
      </FormLayout>
    </div>
  )
}
