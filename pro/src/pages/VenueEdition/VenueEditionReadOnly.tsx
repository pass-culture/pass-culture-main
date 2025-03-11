import { GetVenueResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { OpeningHoursReadOnly } from 'pages/VenueEdition/OpeningHoursReadOnly/OpeningHoursReadOnly'

import { AccessibilityReadOnly } from './AccessibilityReadOnly/AccessibilityReadOnly'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')

  const PublicWelcomeSection = ({ children }: { children: React.ReactNode | React.ReactNode[] }): JSX.Element => {
    return isOpenToPublicEnabled ?
      <SummarySubSection
        title="Accueil du public"
        shouldShowDivider={false}
      >
        {children}
      </SummarySubSection> : <>{children}</>
  }

  return (
    <SummarySection
      title="Vos informations pour le grand public"
      editLink={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/edition`}
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
        {isOpenToPublicEnabled && !venue.isOpenToPublic && <span>
          Accueil du public dans la structure : Non
        </span>}
        {(!isOpenToPublicEnabled || venue.isOpenToPublic) && <>
          <OpeningHoursReadOnly
            isOpenToPublicEnabled={isOpenToPublicEnabled}
            openingHours={venue.openingHours}
            address={venue.address}
          />
          <AccessibilityReadOnly
            isOpenToPublicEnabled={isOpenToPublicEnabled}
            venue={venue}
          />
        </>}
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
