import { GetVenueResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { OpeningHoursReadOnly } from 'pages/VenueEdition/OpeningHoursReadOnly/OpeningHoursReadOnly'

import { AccessibilityReadOnly } from './AccessibilityReadOnly/AccessibilityReadOnly'
import { getPathToNavigateTo } from './context'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  const isOpenToPublicEnabled = true

  const PublicWelcomeSection = ({
    children,
  }: {
    children: React.ReactNode | React.ReactNode[]
  }): JSX.Element => {
    return (
      <SummarySubSection title="Accueil du public" shouldShowDivider={false}>
        {children}
      </SummarySubSection>
    )
  }

  return (
    <SummarySection
      title="Vos informations pour le grand public"
      editLink={getPathToNavigateTo(venue.managingOfferer.id, venue.id, true)}
    >
      <SummarySubSection
        title="À propos de votre activité"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Description',
              text: venue.description ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
      <PublicWelcomeSection>
        {!venue.isOpenToPublic && (
          <span>Accueil du public dans la structure : Non</span>
        )}
        {venue.isOpenToPublic && (
          <>
            <OpeningHoursReadOnly
              isOpenToPublicEnabled={isOpenToPublicEnabled}
              openingHours={venue.openingHours}
              address={venue.address}
            />
            <AccessibilityReadOnly
              isOpenToPublicEnabled={isOpenToPublicEnabled}
              venue={venue}
            />
          </>
        )}
      </PublicWelcomeSection>
      <SummarySubSection
        title="Informations de contact"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Téléphone',
              text: venue.contact?.phoneNumber ?? 'Non renseigné',
            },
            {
              title: 'Adresse e-mail',
              text: venue.contact?.email ?? 'Non renseignée',
            },
            {
              title: 'URL de votre site web',
              text: venue.contact?.website ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
    </SummarySection>
  )
}
