import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { toStringOrNull } from '@/commons/utils/toStringOrNull'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import { mapVenueDomains } from '../utils/mapVenueDomains'

export const ActivitySubSection = () => {
  const { data: educationalDomains } = useEducationalDomains()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const venueDomains = mapVenueDomains(selectedPartnerVenue, educationalDomains)

  return (
    <SummarySubSection
      title="À propos de votre activité"
      shouldShowDivider={false}
    >
      <SummaryDescriptionList
        descriptions={[
          ...(selectedPartnerVenue.activity
            ? [
                {
                  title: 'Activité',
                  text: getActivityLabel(selectedPartnerVenue.activity),
                },
              ]
            : []),
          {
            title: pluralizeFr(
              venueDomains.length,
              'Domaine d’activité',
              'Domaines d’activité'
            ),
            text: venueDomains.join(', '),
          },
          {
            title: 'Description',
            text:
              toStringOrNull(selectedPartnerVenue.description) ??
              'Non renseignée',
          },
        ]}
      />
    </SummarySubSection>
  )
}
