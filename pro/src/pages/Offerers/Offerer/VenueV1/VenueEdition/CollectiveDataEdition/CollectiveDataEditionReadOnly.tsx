import type { GetVenueResponseModel } from '@/apiClient/v1'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { getInterventionAreaLabels } from '@/pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/utils/getInterventionAreaLabels'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

interface CollectiveDataEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const CollectiveDataEditionReadOnly = ({
  venue,
}: CollectiveDataEditionReadOnlyProps) => {
  return (
    <SummarySection
      title="Vos informations pour les enseignants"
      editLink={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/collectif/edition`}
    >
      <SummarySubSection title="Présentation pour les enseignants">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Démarche d’éducation artistique et culturelle',
              text: venue.collectiveDescription ?? 'Non renseignée',
            },
            {
              title: 'Public cible',
              text: venue.collectiveStudents?.join(', ') ?? 'Non renseignée',
            },
            {
              title: 'URL de votre site web',
              text: venue.collectiveWebsite ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>

      <SummarySubSection title="Informations de la structure">
        <SummaryDescriptionList
          descriptions={[
            ...(venue.activity
              ? [
                  {
                    title: 'Activité',
                    text: getActivityLabel(venue.activity),
                  },
                ]
              : []),
            {
              title: pluralizeFr(
                venue.collectiveDomains.length,
                'Domaine artistique et culturel',
                'Domaines artistiques et culturels'
              ),
              text:
                venue.collectiveDomains.length > 0
                  ? venue.collectiveDomains
                      .map((domain) => domain.name)
                      .join(', ')
                  : 'Non renseigné',
            },
            {
              title: pluralizeFr(
                venue.collectiveInterventionArea?.length ?? 0,
                'Zone de mobilité',
                'Zones de mobilité'
              ),
              text: venue.collectiveInterventionArea?.length
                ? getInterventionAreaLabels(venue.collectiveInterventionArea)
                : 'Non renseignée',
            },
            {
              title: 'Statut',
              text: venue.collectiveLegalStatus?.name ?? 'Non renseigné',
            },
          ]}
        />
      </SummarySubSection>

      <SummarySubSection title="Contact">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Téléphone',
              text: venue.collectivePhone ?? 'Non renseigné',
            },
            {
              title: 'Adresse e-mail',
              text: venue.collectiveEmail ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
    </SummarySection>
  )
}
