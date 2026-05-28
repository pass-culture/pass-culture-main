import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { formatPhoneNumber } from '@/commons/utils/formatPhoneNumber'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import { AccessibilityReadOnly } from './AccessibilityReadOnly/AccessibilityReadOnly'
import { ActivityDetailsReadOnly } from './ActivityDetails/ActivityDetailsReadOnly/ActivityDetailsReadOnly'
import { OpeningHoursAndAddressReadOnly } from './OpeningHoursAndAddressReadOnly/OpeningHoursAndAddressReadOnly'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  return (
    <SummarySection
      title="Vos informations"
      editLink={getVenuePagePathToNavigateTo('/edition')}
    >
      <SummarySubSection
        title="À propos de votre activité"
        shouldShowDivider={false}
      >
        <ActivityDetailsReadOnly venue={venue}></ActivityDetailsReadOnly>
      </SummarySubSection>
      {venue.isOpenToPublic && (
        <>
          <OpeningHoursAndAddressReadOnly
            openingHours={venue.openingHours}
            address={venue.location}
          />
          <AccessibilityReadOnly venue={venue} />
        </>
      )}
      <SummarySubSection
        title="Informations de retrait de vos offres"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Informations de retrait',
              text: venue.withdrawalDetails || 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
      <SummarySubSection title="Bénévolat" shouldShowDivider={false}>
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Lien vers votre page organisation JeVeuxAider.gouv.fr',
              text: venue.volunteeringUrl || 'Non renseigné',
            },
          ]}
        />
      </SummarySubSection>
      <SummarySubSection
        title="Informations de contact"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Téléphone',
              text:
                formatPhoneNumber(venue.contact?.phoneNumber) ||
                'Non renseigné',
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
