import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { getError, isErrorAPIError } from '@/apiClient/helpers'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullCloseIcon from '@/icons/full-close.svg'
import strokeBarcodeIcon from '@/icons/stroke-barcode.svg'
import type { Product } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { eanSearchValidationSchema } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'
import { EanSearchCallout } from '@/pages/IndividualOffer/IndividualOfferDetails/components/EanSearchCallout/EanSearchCallout'

import styles from './DetailsEanSearch.module.scss'

type EanSearchForm = {
  eanSearch?: string
}

export type DetailsEanSearchProps = {
  isDraftOffer: boolean
  isProductBased: boolean
  subcategoryId: string
  initialEan?: string
  eanSubmitError?: string
  onEanSearch: (ean: string, product: Product) => void
  onEanReset: () => void
}

export const DetailsEanSearch = ({
  isDraftOffer,
  isProductBased,
  subcategoryId,
  initialEan,
  eanSubmitError,
  onEanSearch,
  onEanReset,
}: DetailsEanSearchProps): JSX.Element => {
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const [wasCleared, setWasCleared] = useState(false)
  const [subcatError, setSubcatError] = useState<string | null>(null)

  const isDraftOfferProductBased = isDraftOffer && isProductBased
  const isDraftOfferNotProductBased = isDraftOffer && !isProductBased

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
    resolver: yupResolver<EanSearchForm, unknown, unknown>(
      eanSearchValidationSchema
    ),
    mode: 'onChange',
  })

  const ean = watch('eanSearch', '')

  useEffect(() => {
    if (wasCleared) {
      setFocus('eanSearch')
      setWasCleared(false)
    }
  }, [wasCleared, setFocus])

  useEffect(() => {
    if (eanSubmitError) {
      setError('eanSearch', {
        type: 'apiError',
        message: eanSubmitError,
      })
    }
  }, [eanSubmitError, setError])

  useEffect(() => {
    if (isDraftOfferNotProductBased && isSubCategoryCD(subcategoryId)) {
      setSubcatError('Les offres de type CD doivent être liées à un produit.')
    } else {
      setSubcatError(null)
    }
  }, [isDraftOfferNotProductBased, subcategoryId])

  const onSearch = async (data: EanSearchForm) => {
    if (data.eanSearch) {
      try {
        assertOrFrontendError(
          selectedOffererId,
          'Offerer should have already been selected.'
        )

        const product = await api.getProductByEan(
          data.eanSearch,
          selectedOffererId
        )
        onEanSearch(data.eanSearch, product)
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

  const apiError = errors.eanSearch?.type === 'apiError'
  const shouldInputBeDisabled = isProductBased || isLoading
  const shouldInputBeRequired = !!subcatError

  const shouldButtonBeDisabled =
    isProductBased || !ean || !isValid || !!apiError || isLoading
  const displayClearButton = isDraftOfferProductBased

  const cumulativeError = subcatError
    ? `${subcatError}\n${errors.eanSearch?.message || ''}`
    : errors.eanSearch?.message || ''

  return (
    <form onSubmit={handleSubmit(onSearch)}>
      <FormLayout fullWidthActions>
        <div className={styles['details-ean-search']}>
          <div className={styles['details-ean-search-container']}>
            <TextInput
              label="Scanner ou rechercher un produit par EAN"
              error={cumulativeError}
              disabled={shouldInputBeDisabled}
              required={shouldInputBeRequired}
              description="Format : EAN à 13 chiffres"
              {...(!displayClearButton
                ? {
                    icon: strokeBarcodeIcon,
                  }
                : {
                    iconButton: {
                      icon: fullCloseIcon,
                      label: 'Effacer',
                      onClick: onEanClear,
                      disabled: isLoading,
                    },
                  })}
              {...register('eanSearch')}
              maxCharactersCount={13}
              extension={
                <Button
                  type="submit"
                  disabled={shouldButtonBeDisabled}
                  label="Rechercher"
                />
              }
            />
          </div>
        </div>
        {/** biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`. */}
        <div role="status" className={styles['details-ean-search-callout']}>
          {isProductBased && <EanSearchCallout isDraftOffer={isDraftOffer} />}
        </div>
      </FormLayout>
    </form>
  )
}
