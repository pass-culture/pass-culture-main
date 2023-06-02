import React, { useMemo } from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'

import { DEFAULT_RECAP_VALUE } from '../constants'
import { formatDuration } from '../utils/formatDuration'

interface CollectiveOfferSummaryProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
}

const CollectiveOfferTypeSection = ({
  offer,
  categories,
}: CollectiveOfferSummaryProps) => {
  const subCategory = useMemo(
    () =>
      categories.educationalSubCategories.find(
        subCategory => subCategory.id === offer.subcategoryId
      ),
    [offer.subcategoryId]
  )

  const category = useMemo(() => {
    if (subCategory) {
      return categories.educationalCategories.find(
        category => category.id === subCategory.categoryId
      )
    }

    return
  }, [offer.subcategoryId])

  return (
    <SummaryLayout.SubSection title="Type d’offre">
      <SummaryLayout.Row
        title="Catégorie"
        description={category?.label || DEFAULT_RECAP_VALUE}
      />
      <SummaryLayout.Row
        title="Sous-catégorie"
        description={subCategory?.label || DEFAULT_RECAP_VALUE}
      />
      <SummaryLayout.Row
        title="Domaine artistiques et culturels"
        description={offer.domains.map(domain => domain.name).join(', ')}
      />
      <SummaryLayout.Row title="Titre de l’offre" description={offer.name} />
      <SummaryLayout.Row
        title="Description"
        description={offer.description || DEFAULT_RECAP_VALUE}
      />
      <SummaryLayout.Row
        title="Durée"
        description={formatDuration(offer.durationMinutes)}
      />
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferTypeSection
