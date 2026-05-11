import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { getInterventionAreaLabels } from '@/pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/utils/getInterventionAreaLabels'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

export const CollectiveDataEditionReadOnly = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  return (
    <SummarySection
      title="Vos informations pour les enseignants"
      editLink={`/partenaire/page-collective/edition`}
    >
      <SummarySubSection title="Présentation pour les enseignants">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Démarche d’éducation artistique et culturelle',
              text:
                selectedPartnerVenue.collectiveDescription ?? 'Non renseignée',
            },
            {
              title: 'Public cible',
              text:
                selectedPartnerVenue.collectiveStudents?.join(', ') ??
                'Non renseignée',
            },
            {
              title: 'URL de votre site web',
              text: selectedPartnerVenue.collectiveWebsite ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>

      <SummarySubSection title="Informations de la structure">
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
                selectedPartnerVenue.collectiveDomains.length,
                'Domaine artistique et culturel',
                'Domaines artistiques et culturels'
              ),
              text:
                selectedPartnerVenue.collectiveDomains.length > 0
                  ? selectedPartnerVenue.collectiveDomains
                      .map((domain) => domain.name)
                      .join(', ')
                  : 'Non renseigné',
            },
            {
              title: pluralizeFr(
                selectedPartnerVenue.collectiveInterventionArea?.length ?? 0,
                'Zone de mobilité',
                'Zones de mobilité'
              ),
              text: selectedPartnerVenue.collectiveInterventionArea?.length
                ? getInterventionAreaLabels(
                    selectedPartnerVenue.collectiveInterventionArea
                  )
                : 'Non renseignée',
            },
            {
              title: 'Statut',
              text:
                selectedPartnerVenue.collectiveLegalStatus?.name ??
                'Non renseigné',
            },
          ]}
        />
      </SummarySubSection>

      <SummarySubSection title="Contact">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Téléphone',
              text: selectedPartnerVenue.collectivePhone ?? 'Non renseigné',
            },
            {
              title: 'Adresse e-mail',
              text: selectedPartnerVenue.collectiveEmail ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
    </SummarySection>
  )
}
