import { useFormikContext } from 'formik'
import { useState } from 'react'

import {
  GetOffererResponseModel,
  SharedCurrentUserResponseModel,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { AddressSelect } from 'components/Address/Address'
import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  RouteLeavingGuard,
  BlockerFunction,
} from 'components/RouteLeavingGuard/RouteLeavingGuard'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { Banner } from 'ui-kit/Banners/Banner/Banner'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Select } from 'ui-kit/form/Select/Select'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { Accessibility } from './Accessibility/Accessibility'
import { buildVenueTypesOptions } from './buildVenueTypesOptions'
import { SiretOrCommentFields } from './SiretOrCommentFields/SiretOrCommentFields'
import { VenueCreationFormValues } from './types'
import styles from './VenueCreationForm.module.scss'
import { venueSubmitRedirectUrl } from './venueSubmitRedirectUrl'

type VenueFormProps = {
  offerer: GetOffererResponseModel
  updateIsSiretValued: (isSiretValued: boolean) => void
  venueTypes: VenueTypeResponseModel[]
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
  const { initialValues, isSubmitting } =
    useFormikContext<VenueCreationFormValues>()
  const user = useCurrentUser()

  const [isFieldNameFrozen, setIsFieldNameFrozen] = useState(false)
  const [isSiretValued, setIsSiretValued] = useState(true)
  const canOffererCreateCollectiveOffer = offerer.allowedOnAdage
  const venueTypesOptions = buildVenueTypesOptions(venueTypes)

  return (
    <div>
      <ScrollToFirstErrorAfterSubmit />

      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />

        <FormLayout.Section title="Informations du lieu">
          <FormLayout.Row>
            <SiretOrCommentFields
              initialSiret={initialValues.siret}
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
                ...venueTypesOptions,
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
          >
            <p className={styles['eac-description-info']}>
              Il s’agit d’un formulaire vous permettant de renseigner vos
              informations EAC. Les informations renseignées seront visibles par
              les enseignants et chefs d’établissement sur ADAGE (Application
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

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: '/accueil',
              isExternal: false,
            }}
          >
            Annuler et quitter
          </ButtonLink>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button type="submit" isLoading={isSubmitting}>
            Enregistrer et créer le lieu
          </Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </div>
  )
}
