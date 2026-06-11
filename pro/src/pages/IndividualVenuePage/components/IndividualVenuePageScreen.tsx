import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { formatPhoneNumber } from '@/commons/utils/formatPhoneNumber'
import { toStringOrNull } from '@/commons/utils/toStringOrNull'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import { AccessibilitySubSection } from './AccessibilitySubSection'
import { ActivitySubSection } from './ActivitySubSection'
import { AddressAndOpeningHourSubSection } from './AddressAndOpeningHourSubSection/AddressAndOpeningHourSubSection'

export const IndividualVenuePageScreen = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  return (
    <SummarySection
      title="Vos informations"
      editLink="/partenaire/page-partenaire/edition"
    >
      <ActivitySubSection />

      {selectedPartnerVenue.isOpenToPublic && (
        <>
          <AddressAndOpeningHourSubSection
            openingHours={selectedPartnerVenue.openingHours}
            address={selectedPartnerVenue.location}
          />
          <AccessibilitySubSection />
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
              text:
                toStringOrNull(selectedPartnerVenue.withdrawalDetails) ??
                'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>

      <SummarySubSection title="Bénévolat" shouldShowDivider={false}>
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Lien vers votre page organisation JeVeuxAider.gouv.fr',
              text:
                toStringOrNull(selectedPartnerVenue.volunteeringUrl) ??
                'Non renseigné',
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
                toStringOrNull(
                  formatPhoneNumber(selectedPartnerVenue.contact?.phoneNumber)
                ) ?? 'Non renseigné',
            },
            {
              title: 'Adresse e-mail',
              text:
                toStringOrNull(selectedPartnerVenue.contact?.email) ??
                'Non renseignée',
            },
            {
              title: 'URL de votre site web',
              text:
                toStringOrNull(selectedPartnerVenue.contact?.website) ??
                'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
    </SummarySection>
  )
}
