import * as Sentry from '@sentry/react'
import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import { AddressSelect } from 'components/Address'
import FormLayout from 'components/FormLayout'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useNotification from 'hooks/useNotification'
import { TextInput, InfoBox, Select, Banner } from 'ui-kit'

import RouteLeavingGuard, {
  BlockerFunction,
} from '../../components/RouteLeavingGuard'
import useCurrentUser from '../../hooks/useCurrentUser'

import { Accessibility } from './Accessibility/Accessibility'
import { SiretOrCommentFields } from './SiretOrCommentFields/SiretOrCommentFields'
import { VenueCreationFormValues } from './types'
import styles from './VenueCreationForm.module.scss'
import { VenueFormActionBar } from './VenueFormActionBar'
import { venueSubmitRedirectUrl } from './venueSubmitRedirectUrl'

type VenueFormProps = {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: SelectOption[]
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
    const url = venueSubmitRedirectUrl(offererId, user)
    const nextUrl = nextLocation.pathname + nextLocation.search

    return !nextUrl.startsWith(url)
  }

export const VenueCreationForm = ({
  offerer,
  updateIsSiretValued,
  venueTypes,
}: VenueFormProps) => {
  const { initialValues } = useFormikContext<VenueCreationFormValues>()
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

          <FormLayout.Row>
            <TextInput
              name="name"
              label="Raison sociale"
              disabled={isFieldNameFrozen}
            />
          </FormLayout.Row>

          <FormLayout.Row
            sideComponent={
              <InfoBox>
                À remplir si différent de la raison sociale. En le remplissant,
                c’est ce dernier qui sera visible du public.
              </InfoBox>
            }
          >
            <TextInput name="publicName" label="Nom public" isOptional />
          </FormLayout.Row>
        </FormLayout.Section>

        <FormLayout.Section
          title="Adresse de l’activité"
          description="Cette adresse sera utilisée pour permettre aux jeunes de géolocaliser votre lieu."
        >
          <FormLayout.Row>
            <AddressSelect />
          </FormLayout.Row>
        </FormLayout.Section>

        <FormLayout.Section
          title="Activité"
          description="Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu."
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
            />
          </FormLayout.Row>
        </FormLayout.Section>

        <Accessibility isCreatingVenue />

        <FormLayout.Section title="Notifications de réservations">
          <FormLayout.Row
            sideComponent={
              <InfoBox>
                Cette adresse s’appliquera par défaut à toutes vos offres, vous
                pourrez la modifier à l’échelle de chaque offre.
              </InfoBox>
            }
          >
            <TextInput
              name="bookingEmail"
              label="Adresse email"
              type="email"
              placeholder="email@exemple.com"
            />
          </FormLayout.Row>
        </FormLayout.Section>

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
            <p className={styles['eac-description-info']}>
              Il s’agit d’un formulaire vous permettant de renseigner vos
              informations EAC. Les informations renseignées seront visibles par
              les enseignants et chefs d’établissement sur Adage (Application
              dédiée à la généralisation....)
            </p>

            <Banner type="notification-info">
              Une fois votre lieu créé, vous pourrez renseigner des informations
              pour les enseignants en revenant sur cette page.
            </Banner>
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
