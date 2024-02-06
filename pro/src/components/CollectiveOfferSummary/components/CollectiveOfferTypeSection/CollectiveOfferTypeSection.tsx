import React, { useMemo } from 'react'

import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
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
      <SummarySubSection title="Type d’offre">
        {isFormatActive ? (
          <SummaryRow
            title="Format"
            description={offer.formats?.join(', ') || DEFAULT_RECAP_VALUE}
          />
        ) : (
          <>
            <SummaryRow
              title="Catégorie"
              description={category?.label || DEFAULT_RECAP_VALUE}
            />
            <SummaryRow
              title="Sous-catégorie"
              description={subCategory?.label || DEFAULT_RECAP_VALUE}
            />
          </>
        )}

        <SummaryRow
          title="Domaine artistique et culturel"
          description={offer.domains.map((domain) => domain.name).join(', ')}
        />
        <SummaryRow
          title="Dispositif national"
          description={offer.nationalProgram?.name || DEFAULT_RECAP_VALUE}
        />
      </SummarySubSection>
      <SummarySubSection title="Informations artistiques">
        <SummaryRow title="Titre de l’offre" description={offer.name} />
        <SummaryRow
          title="Description"
          description={offer.description || DEFAULT_RECAP_VALUE}
        />
        <SummaryRow
          title="Durée"
          description={formatDuration(offer.durationMinutes)}
        />
      </SummarySubSection>
    </>
  )
}
