import { useState } from 'react'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  ListOffersOfferResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { GET_CATEGORIES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './DraftOffers.module.scss'

interface DraftOffersProps {
  offers: ListOffersOfferResponseModel[]
  onDraftChange: (offer: ListOffersOfferResponseModel) => void
}

const extractOfferCategoriesData = (
  offer: ListOffersOfferResponseModel,
  categories: CategoryResponseModel[],
  subcategories: SubcategoryResponseModel[]
) => {
  const subcategory = subcategories.find((s) => s.id === offer.subcategoryId)
  const category = categories.find((c) => c.id === subcategory?.categoryId)
  return { category, subcategory }
}

export const DraftOffers = ({
  offers,
  onDraftChange,
}: DraftOffersProps): JSX.Element => {
  const [selectedDraftId, setSelectedDraftId] = useState<null | string>(null)

  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  if (categoriesQuery.isLoading) {
    return <Spinner />
  }

  const categories = categoriesQuery.data.categories
  const subcategories = categoriesQuery.data.subcategories

  const onSelectDraft = (offer: ListOffersOfferResponseModel) => {
    return (event: React.ChangeEvent<HTMLInputElement>) => {
      setSelectedDraftId(event.target.value)
      onDraftChange(offer)
    }
  }

  return (
    <>
      <h2 className={styles['title-drafts']}>
        Reprendre une offre déjà commencée
      </h2>

      {offers.map((offer) => {
        const { category, subcategory } = extractOfferCategoriesData(
          offer,
          categories,
          subcategories
        )
        const categoryLabel = `${category?.proLabel} -> ${subcategory?.proLabel}`

        return (
          <RadioButtonWithImage
            className={styles['offer']}
            key={offer.id}
            name={`draft_${offer.id}`}
            isChecked={Number(selectedDraftId) === offer.id}
            label={offer.name}
            description={categoryLabel}
            onChange={onSelectDraft(offer)}
            value={String(offer.id)}
          />
        )
      })}
    </>
  )
}
