import React, { useMemo } from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'

import { DEFAULT_RECAP_VALUE } from '../constants'
import { formatDuration } from '../utils/formatDuration'

interface CollectiveOfferSummaryProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
}

export default function CollectiveOfferTypeSection({
  offer,
  categories,
}: CollectiveOfferSummaryProps) {
  const subCategory = useMemo(
    () =>
      categories.educationalSubCategories.find(
        (subCategory) => subCategory.id === offer.subcategoryId
      ),
    [offer.subcategoryId]
  )

  const category = useMemo(() => {
    if (subCategory) {
      return categories.educationalCategories.find(
        (category) => category.id === subCategory.categoryId
      )
    }

    return
  }, [offer.subcategoryId])
  const isFormatActive = useActiveFeature('WIP_ENABLE_FORMAT')
  return (
    <>
      <SummaryLayout.SubSection title="Type d’offre">
        {isFormatActive ? (
          <SummaryLayout.Row
            title="Format"
            description={offer.formats?.join(', ') || DEFAULT_RECAP_VALUE}
          />
        ) : (
          <>
            <SummaryLayout.Row
              title="Catégorie"
              description={category?.label || DEFAULT_RECAP_VALUE}
            />
            <SummaryLayout.Row
              title="Sous-catégorie"
              description={subCategory?.label || DEFAULT_RECAP_VALUE}
            />
          </>
        )}

        <SummaryLayout.Row
          title="Domaine artistique et culturel"
          description={offer.domains.map((domain) => domain.name).join(', ')}
        />
        <SummaryLayout.Row
          title="Dispositif national"
          description={offer.nationalProgram?.name || DEFAULT_RECAP_VALUE}
        />
      </SummaryLayout.SubSection>
      <SummaryLayout.SubSection title="Informations artistiques">
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
    </>
  )
}
