import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import { DisplayableActivityMap } from '@/commons/mappings/DisplayableActivity'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'

import { mapVenueDomains } from '../activityDomainsHelper'

interface ActivityDetailsReadOnlyProps {
  venue: GetVenueResponseModel
  isEditionMode?: boolean
}

export const ActivityDetailsReadOnly = ({
  venue,
  isEditionMode = false,
}: ActivityDetailsReadOnlyProps) => {
  const { data: educationalDomains } = useEducationalDomains()

  const venueDomains = mapVenueDomains(venue, educationalDomains)

  return (
    <SummaryDescriptionList
      descriptions={[
        ...(venue.activity
          ? [
              {
                title: 'Activité',
                text: DisplayableActivityMap.get(venue.activity),
              },
            ]
          : []),
        ...(venueDomains
          ? [
              {
                title: pluralizeFr(
                  venueDomains.length,
                  'Domaine d’activité',
                  'Domaines d’activité'
                ),
                text: venueDomains.join(', '),
              },
            ]
          : []),
        ...(isEditionMode
          ? []
          : [
              {
                title: 'Description',
                text: venue.description ?? 'Non renseignée',
              },
            ]),
      ]}
    />
  )
}
