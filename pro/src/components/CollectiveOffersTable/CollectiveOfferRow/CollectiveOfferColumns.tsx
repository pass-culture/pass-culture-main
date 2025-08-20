import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
} from '@/apiClient/v1'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { computeVenueDisplayName } from '@/repository/venuesService'
import type { Column } from '@/ui-kit/Table/Table'

import { CollectiveActionsCells } from './CollectiveActionsCells/CollectiveActionsCells'
import styles from './CollectiveOfferColumns.module.scss'
import { OfferEventDateCell } from './OfferEventDateCell/OfferEventDateCell'
import { OfferNameCell } from './OfferNameCell/OfferNameCell'

export function getCollectiveOfferColumns(
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
): Column<CollectiveOfferResponseModel>[] {
  const isNewCollectiveOfferDetailPageActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE'
  )

  const columns: Column<CollectiveOfferResponseModel>[] = [
    {
      id: 'name',
      label: 'Nom de l’offre',
      render: (offer) => {
        const isOfferDraft =
          offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
          `/offre/collectif/${offer.id}/creation`

        const offerLink =
          isNewCollectiveOfferDetailPageActive && !offer.isShowcase
            ? `/offre/${offer.id}/collectif/recapitulatif`
            : isOfferDraft || `/offre/${offer.id}/collectif/recapitulatif`

        return <OfferNameCell offer={offer} offerLink={offerLink} />
      },
    },
    {
      id: 'dates',
      label: 'Date de l’évènement',
      sortable: true,
      ordererField: 'dates',
      render: (offer) => <OfferEventDateCell offer={offer} />,
    },
    {
      id: 'venue',
      label: 'Structure',
      render: (offer) => (
        <span className={styles['structure-cell']}>
          {computeVenueDisplayName(offer.venue)}
        </span>
      ),
    },
    {
      id: 'educationalInstitution',
      label: 'Publication',
      render: (offer) => {
        const { name, institutionType, city } =
          offer.educationalInstitution || {}

        let showEducationalInstitution = 'Tous les établissements'

        if (name) {
          showEducationalInstitution = name
        } else if (institutionType || city) {
          showEducationalInstitution = `${institutionType} ${city}`
        }

        return showEducationalInstitution
      },
    },
    {
      id: 'status',
      label: 'Statut',
      render: (offer) => (
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      ),
    },
    {
      id: 'actions',
      label: 'Actions',
      render: (offer) => {
        const isOfferDraft =
          offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
          `/offre/collectif/${offer.id}/creation`

        const editionOfferLink =
          isOfferDraft || `/offre/${offer.id}/collectif/edition`

        return (
          <CollectiveActionsCells
            offer={offer}
            editionOfferLink={editionOfferLink}
            urlSearchFilters={urlSearchFilters}
          />
        )
      },
    },
  ]

  return columns
}
