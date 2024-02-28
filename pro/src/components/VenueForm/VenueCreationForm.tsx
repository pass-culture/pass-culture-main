import * as Sentry from '@sentry/react'
import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  SharedCurrentUserResponseModel,
  VenueProviderResponse,
} from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { Providers } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useNotification from 'hooks/useNotification'
import { venueSubmitRedirectUrl } from 'screens/VenueForm/utils/venueSubmitRedirectUrl'
import { TextInput, InfoBox, Select } from 'ui-kit'

import useCurrentUser from '../../hooks/useCurrentUser'
import RouteLeavingGuard, { BlockerFunction } from '../RouteLeavingGuard'

import { Accessibility } from './Accessibility'
import { Contact } from './Contact'
import { EACInformation } from './EACInformation/EACInformation'
import { ImageUploaderVenue } from './ImageUploaderVenue'
import SiretOrCommentFields from './Informations/SiretOrCommentFields'
import { VenueFormActionBar } from './VenueFormActionBar'

import { VenueFormValues } from '.'

type VenueFormProps = {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
  provider?: Providers[]
  venueProvider?: VenueProviderResponse[]
  initialIsVirtual?: boolean
}

type ShouldBlockVenueNavigationProps = {
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
  initialIsVirtual = false,
}: VenueFormProps) => {
  const {
    initialValues,
    values: { isPermanent },
  } = useFormikContext<VenueFormValues>()
  const shouldDisplayImageVenueUploaderSection = isPermanent
  useScrollToFirstErrorAfterSubmit()
  const user = useCurrentUser()

  const [canOffererCreateCollectiveOffer, setCanOffererCreateCollectiveOffer] =
    useState(false)
  const [isFieldNameFrozen, setIsFieldNameFrozen] = useState(false)
  const [isSiretValued, setIsSiretValued] = useState(true)
  const notify = useNotification()
  useEffect(() => {
    const loadCanOffererCreateCollectiveOffer = async () => {
      try {
        const { canCreate } = await api.canOffererCreateEducationalOffer(
          offerer.id
        )
        setCanOffererCreateCollectiveOffer(canCreate)
      } catch (error) {
        notify.error(GET_DATA_ERROR_MESSAGE)
        Sentry.captureException(error)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadCanOffererCreateCollectiveOffer()
  }, [offerer.id, notify])

  return (
    <div>
      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />

        <FormLayout.Section title="Informations du lieu">
          {!initialIsVirtual && (
            <FormLayout.Row>
              <SiretOrCommentFields
                initialSiret={initialValues.siret}
                readOnly={Boolean(initialValues.siret)}
                isToggleDisabled={false}
                isCreatedEntity
                setIsFieldNameFrozen={setIsFieldNameFrozen}
                setIsSiretValued={setIsSiretValued}
                updateIsSiretValued={updateIsSiretValued}
                siren={offerer.siren}
              />
            </FormLayout.Row>
          )}

          <FormLayout.Row>
            <TextInput
              name="name"
              label="Raison sociale"
              disabled={isFieldNameFrozen || initialIsVirtual}
            />
          </FormLayout.Row>

          {!initialIsVirtual && (
            <FormLayout.Row
              sideComponent={
                <InfoBox>
                  À remplir si différent de la raison sociale. En le
                  remplissant, c’est ce dernier qui sera visible du public.
                </InfoBox>
              }
            >
              <TextInput name="publicName" label="Nom public" isOptional />
            </FormLayout.Row>
          )}
        </FormLayout.Section>

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

        <FormLayout.Section
          title="Activité"
          description={
            initialIsVirtual
              ? undefined
              : 'Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu.'
          }
        >
          <FormLayout.Row>
            <Select
              options={[
                {
                  value: '',
                  label: 'Sélectionnez celui qui correspond à votre lieu',
                },
                ...venueTypes,
              ]}
              name="venueType"
              label="Activité principale"
              disabled={initialIsVirtual}
            />
          </FormLayout.Row>
        </FormLayout.Section>

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
      </FormLayout>
      <VenueFormActionBar isCreatingVenue={true} />
    </div>
  )
}
