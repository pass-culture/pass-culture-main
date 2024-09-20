import { useFormikContext } from 'formik'
import { useState, useRef, useEffect } from 'react'
import { useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { isErrorAPIError, getError } from 'apiClient/helpers'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferImage } from 'core/Offers/types'
import strokeBarcode from 'icons/stroke-barcode.svg'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Button } from 'ui-kit/Button/Button'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { EanSearchCallout } from '../EanSearchCallout/EanSearchCallout'
import { DetailsFormValues } from '../types'
import { hasMusicType, isSubCategoryCDOrVinyl } from '../utils'

import styles from './DetailsEanSearch.module.scss'

export type DetailsEanSearchProps = {
  setImageOffer: (imageOffer: IndividualOfferImage) => void
  isOfferProductBased: boolean
}

export const DetailsEanSearch = ({
  setImageOffer,
  isOfferProductBased,
}: DetailsEanSearchProps): JSX.Element => {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const inputRef = useRef<HTMLInputElement>(null)
  const [isFetchingProduct, setIsFetchingProduct] = useState(false)
  const [subcatError, setSubcatError] = useState<string | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [wasCleared, setWasCleared] = useState(false)

  const { subCategories } = useIndividualOfferContext()
  const {
    values,
    errors: { eanSearch: formikError },
    setValues,
    resetForm,
  } = useFormikContext<DetailsFormValues>()
  const { eanSearch: ean, productId, subcategoryId } = values

  const isDirtyDraftOfferProductBased = !isOfferProductBased && !!productId
  const isProductBased = isOfferProductBased || isDirtyDraftOfferProductBased

  useEffect(() => {
    setApiError(null)
  }, [ean])

  useEffect(() => {
    if (wasCleared && inputRef.current) {
      inputRef.current.focus()
      setWasCleared(false)
    }
  }, [wasCleared, productId])

  useEffect(() => {
    if (!isProductBased && isSubCategoryCDOrVinyl(subcategoryId)) {
      setSubcatError(
        'Les offres de type CD ou Vinyle doivent être liées à un produit.'
      )
    } else {
      setSubcatError(null)
    }
  }, [subcategoryId, isProductBased])

  const onEanSearch = async () => {
    if (ean) {
      try {
        setIsFetchingProduct(true)
        if (!selectedOffererId) {
          throw new Error('Offerer should have already been selected')
        }
        const res = await api.getProductByEan(ean, selectedOffererId)

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
          ean,
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

  const shouldInputBeDisabled = isProductBased || isFetchingProduct
  const shouldInputBeRequired = !!subcatError
  const shouldButtonBeDisabled =
    isProductBased || !ean || !!formikError || !!apiError || isFetchingProduct
  const displayClearButton = isDirtyDraftOfferProductBased

  const label = (
    <>
      <Tag
        className={styles['details-ean-search-tag']}
        variant={TagVariant.BLUE}
      >
        Nouveau
      </Tag>
      Scanner ou rechercher un produit par EAN
    </>
  )

  const nonFormikError = subcatError || apiError
  const errorArray = [formikError, apiError, subcatError].filter(Boolean)
  const externalError = nonFormikError ? errorArray.join('\n') : undefined

  return (
    <div className={styles['details-ean-search']}>
      <div className={styles['details-ean-search-form']}>
        <TextInput
          refForInput={inputRef}
          classNameLabel={styles['details-ean-search-label']}
          label={label}
          description="Format : EAN à 13 chiffres"
          name="eanSearch"
          type="text"
          disabled={shouldInputBeDisabled}
          maxLength={13}
          isOptional={!shouldInputBeRequired}
          countCharacters
          {...(externalError && {
            externalError,
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
      <div role="status" className={styles['details-ean-search-callout']}>
        {isProductBased && (
          <EanSearchCallout
            isDirtyDraftOfferProductBased={isDirtyDraftOfferProductBased}
          />
        )}
      </div>
    </div>
  )
}
