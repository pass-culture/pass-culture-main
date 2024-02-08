import React, { useMemo } from 'react'

import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
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

  const offerTypeDescriptions: Description[] = []

  if (isFormatActive) {
    offerTypeDescriptions.push({
      title: 'Format',
      text: offer.formats?.join(', ') || DEFAULT_RECAP_VALUE,
    })
  } else {
    offerTypeDescriptions.push(
      { title: 'Catégorie', text: category?.label || DEFAULT_RECAP_VALUE },
      {
        title: 'Sous-catégorie',
        text: subCategory?.label || DEFAULT_RECAP_VALUE,
      }
    )
  }
  offerTypeDescriptions.push({
    title: 'Domaine artistique et culturel',
    text: offer.domains.map((domain) => domain.name).join(', '),
  })
  offerTypeDescriptions.push({
    title: 'Dispositif national',
    text: offer.nationalProgram?.name || DEFAULT_RECAP_VALUE,
  })

  return (
    <>
      <SummarySubSection title="Type d’offre">
        <SummaryDescriptionList descriptions={offerTypeDescriptions} />
      </SummarySubSection>

      <SummarySubSection title="Informations artistiques">
        <SummaryDescriptionList
          descriptions={[
            { title: 'Titre de l’offre', text: offer.name },
            {
              title: 'Description',
              text: offer.description || DEFAULT_RECAP_VALUE,
            },
            { title: 'Durée', text: formatDuration(offer.durationMinutes) },
          ]}
        />
      </SummarySubSection>
    </>
  )
}
