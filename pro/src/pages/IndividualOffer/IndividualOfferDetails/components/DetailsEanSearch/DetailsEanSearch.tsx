import { yupResolver } from '@hookform/resolvers/yup'
import { useState, useEffect, useId } from 'react'
import { useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { isErrorAPIError, getError } from 'apiClient/helpers'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullCloseIcon from 'icons/full-close.svg'
import strokeBarcode from 'icons/stroke-barcode.svg'
import { Product } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { eanSearchValidationSchema } from 'pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'
import { EanSearchCallout } from 'pages/IndividualOffer/IndividualOfferDetails/components/EanSearchCallout/EanSearchCallout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './DetailsEanSearch.module.scss'

type EanSearchForm = {
  eanSearch?: string
}

export type DetailsEanSearchProps = {
  isDirtyDraftOffer: boolean
  productId: string
  subcategoryId: string
  initialEan?: string
  eanSubmitError?: string
  onEanSearch: (ean: string, product: Product) => Promise<void>
  onEanReset: () => void
}

export const DetailsEanSearch = ({
  isDirtyDraftOffer,
  productId,
  subcategoryId,
  initialEan,
  eanSubmitError,
  onEanSearch,
  onEanReset,
}: DetailsEanSearchProps): JSX.Element => {
  const tooltipId = useId()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const [wasCleared, setWasCleared] = useState(false)

  const isProductBased = !!productId
  const isDirtyDraftOfferProductBased = isDirtyDraftOffer && isProductBased
  const isDirtyDraftOfferNotProductBased = isDirtyDraftOffer && !isProductBased

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setError,
    setFocus,
    formState: { errors, isValid, isLoading },
  } = useForm<EanSearchForm>({
    defaultValues: { eanSearch: initialEan || '' },
    resolver: yupResolver(eanSearchValidationSchema),
    mode: 'onBlur',
  })

  const ean = watch('eanSearch', '')

  useEffect(() => {
    if (wasCleared) {
      setFocus('eanSearch')
      setWasCleared(false)
    }
  }, [wasCleared, setFocus])

  useEffect(() => {
    if (isDirtyDraftOfferNotProductBased && isSubCategoryCD(subcategoryId)) {
      setError('eanSearch', {
        type: 'subCatError',
        message: 'Les offres de type CD doivent être liées à un produit.',
      })
    }
  }, [isDirtyDraftOfferNotProductBased, subcategoryId, setError])

  const onSearch = async (data: EanSearchForm) => {
    if (data.eanSearch) {
      try {
        if (!selectedOffererId) {
          throw new Error('Offerer should have already been selected')
        }

        const product = await api.getProductByEan(
          data.eanSearch,
          selectedOffererId
        )
        await onEanSearch(data.eanSearch, product)
      } catch (err) {
        const fallbackMessage = 'Une erreur est survenue lors de la recherche'
        const errorMessage = isErrorAPIError(err)
          ? getError(err).ean?.[0] || fallbackMessage
          : fallbackMessage

        setError('eanSearch', { type: 'apiError', message: errorMessage })
      }
    }
  }

  const onEanClear = () => {
    reset()
    onEanReset()
    setWasCleared(true)
  }

  const apiError = eanSubmitError || errors.eanSearch?.message
  const shouldInputBeDisabled = isProductBased || isLoading
  const shouldInputBeRequired = errors.eanSearch?.type !== 'subCatError'

  const shouldButtonBeDisabled =
    isProductBased || !ean || !isValid || !!apiError || isLoading
  const displayClearButton = isDirtyDraftOfferProductBased

  return (
    <form onSubmit={handleSubmit(onSearch)}>
      <FormLayout fullWidthActions>
        <div className={styles['details-ean-search']}>
          <div className={styles['details-ean-search-form']}>
            <div className={styles['input-container']}>
              <TextInput
                label={'Scanner ou rechercher un produit par EAN'}
                error={errors.eanSearch?.message}
                disabled={shouldInputBeDisabled}
                required={shouldInputBeRequired}
                maxLength={13}
                description="Format : EAN à 13 chiffres"
                {...(!displayClearButton && {
                  rightIcon: strokeBarcode,
                })}
                {...register('eanSearch')}
                count={ean?.length}
              />
              {displayClearButton && (
                <div className={styles['clear-button-container']}>
                  <Button
                    onClick={onEanClear}
                    aria-describedby={tooltipId}
                    className={styles['clear-button']}
                    hasTooltip={true}
                    type="button"
                    icon={fullCloseIcon}
                    variant={ButtonVariant.TERNARY}
                  >
                    Effacer
                  </Button>
                </div>
              )}
            </div>

            <Button
              type="submit"
              className={styles['details-ean-search-button']}
              disabled={shouldButtonBeDisabled}
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
      </FormLayout>
    </form>
  )
}
