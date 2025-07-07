import { GetVenueResponseModel } from 'apiClient/v1'
import { getVenuePagePathToNavigateTo } from 'commons/utils/getVenuePagePathToNavigateTo'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { OpeningHoursReadOnly } from 'pages/VenueEdition/OpeningHoursReadOnly/OpeningHoursReadOnly'

import { AccessibilityReadOnly } from './AccessibilityReadOnly/AccessibilityReadOnly'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

const PublicWelcomeSection = ({
  isOpenToPublicEnabled,
  children,
}: {
  isOpenToPublicEnabled: boolean
  children: React.ReactNode | React.ReactNode[]
}): JSX.Element => {
  return isOpenToPublicEnabled ? (
    <SummarySubSection title="Accueil du public" shouldShowDivider={false}>
      {children}
    </SummarySubSection>
  ) : (
    <>{children}</>
  )
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  const isOpenToPublicEnabled = true

  return (
    <SummarySection
      title="Vos informations pour le grand public"
      editLink={getVenuePagePathToNavigateTo(
        venue.managingOfferer.id,
        venue.id,
        '/edition'
      )}
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
      <PublicWelcomeSection isOpenToPublicEnabled={isOpenToPublicEnabled}>
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
