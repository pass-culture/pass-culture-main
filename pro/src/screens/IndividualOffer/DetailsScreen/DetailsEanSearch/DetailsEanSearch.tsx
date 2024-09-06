import { useFormikContext } from 'formik'
import { useState, useRef, useEffect } from 'react'

import { api } from 'apiClient/api'
import { isErrorAPIError, getError } from 'apiClient/helpers'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferImage } from 'core/Offers/types'
import strokeBarcode from 'icons/stroke-barcode.svg'
import { Button } from 'ui-kit/Button/Button'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { DetailsFormValues } from '../types'
import { hasMusicType } from '../utils'

import styles from './DetailsEanSearch.module.scss'

export type DetailsEanSearchProps = {
  setImageOffer: (imageOffer: IndividualOfferImage) => void
  isClearAvailable?: boolean
}

export const DetailsEanSearch = ({
  setImageOffer,
  isClearAvailable,
}: DetailsEanSearchProps): JSX.Element => {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isFetchingProduct, setIsFetchingProduct] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [wasCleared, setWasCleared] = useState(false)

  const { subCategories } = useIndividualOfferContext()
  const { values, errors, setValues, resetForm } =
    useFormikContext<DetailsFormValues>()
  const { ean, productId } = values

  useEffect(() => {
    setApiError(null)
  }, [ean])

  useEffect(() => {
    if (wasCleared && inputRef.current) {
      inputRef.current.focus()
      setWasCleared(false)
    }
  }, [wasCleared, productId])

  const onEanSearch = async () => {
    if (ean) {
      try {
        setIsFetchingProduct(true)
        const res = await api.getProductByEan(ean)

        const {
          id,
          name,
          description,
          subcategoryId,
          gtlId,
          author,
          performer,
          images,
        } = res

        const subCategory = subCategories.find(
          (subCategory) => subCategory.id === subcategoryId
        )

        if (!subCategory) {
          throw new Error('Unknown or missing subcategoryId')
        }

        const { categoryId, conditionalFields: subcategoryConditionalFields } =
          subCategory

        const imageUrl = images.recto
        if (imageUrl) {
          setImageOffer({
            originalUrl: imageUrl,
            url: imageUrl,
            credit: null,
          })
        }

        let gtl_id = ''
        if (hasMusicType(categoryId, subcategoryConditionalFields)) {
          // Fallback to "Autre" in case of missing gtlId
          // to define "Genre musical" when relevant.
          gtl_id = gtlId || '19000000'
        }

        await setValues({
          ...values,
          name,
          description,
          categoryId,
          subcategoryId,
          gtl_id,
          author,
          performer,
          subcategoryConditionalFields,
          suggestedSubcategory: '',
          productId: id.toString() || '',
        })

        setIsFetchingProduct(false)
      } catch (err) {
        const fallbackMessage = 'Une erreur est survenue lors de la recherche'
        const errorMessage = isErrorAPIError(err)
          ? getError(err).ean?.[0] || fallbackMessage
          : fallbackMessage
        setIsFetchingProduct(false)
        setApiError(errorMessage)
      }
    }
  }

  const onEanClear = () => {
    resetForm()
    setWasCleared(true)
  }

  const isProductBased = !!productId
  const hasInputErrored = !!errors.ean
  const shouldInputBeDisabled = isProductBased || isFetchingProduct
  const shouldButtonBeDisabled =
    isProductBased || !ean || hasInputErrored || !!apiError || isFetchingProduct
  const displayClearButton = isProductBased && isClearAvailable

  const label = (
    <>
      <Tag
        className={styles['details-ean-search-tag']}
        variant={TagVariant.BLUE}
      >
        Nouveau
      </Tag>
      <span>Scanner ou rechercher un produit par EAN</span>
    </>
  )

  return (
    <div className={styles['details-ean-search']}>
      <div className={styles['details-ean-search-form']}>
        <TextInput
          refForInput={inputRef}
          classNameLabel={styles['details-ean-search-label']}
          label={label}
          description="Format : EAN à 13 chiffres"
          name="ean"
          type="text"
          disabled={shouldInputBeDisabled}
          maxLength={13}
          isOptional
          countCharacters
          {...(apiError && {
            externalError: apiError,
          })}
          {...(displayClearButton
            ? {
                clearButtonProps: {
                  tooltip: 'Effacer',
                  display: 'close',
                  onClick: onEanClear,
                },
              }
            : {
                rightIcon: strokeBarcode,
              })}
        />
        <Button
          className={styles['details-ean-search-button']}
          disabled={shouldButtonBeDisabled}
          onClick={onEanSearch}
        >
          Rechercher
        </Button>
      </div>
      <div role="status">
        {isProductBased && (
          <Callout
            className={styles['details-ean-search-callout']}
            variant={CalloutVariant.SUCCESS}
          >
            Les informations suivantes ont été synchronisées à partir de l’EAN
            renseigné.
          </Callout>
        )}
      </div>
    </div>
  )
}
