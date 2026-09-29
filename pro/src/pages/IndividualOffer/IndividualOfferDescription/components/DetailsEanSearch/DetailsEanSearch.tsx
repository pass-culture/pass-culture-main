import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { getError, isErrorAPIError } from '@/apiClient/helpers'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullCloseIcon from '@/icons/full-close.svg'
import strokeBarcodeIcon from '@/icons/stroke-barcode.svg'
import type { Product } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import {
  type EanSearchForm,
  generateEanSearchValidationSchema,
} from '@/pages/IndividualOffer/IndividualOfferDescription/commons/validationSchema'
import { EanSearchCallout } from '@/pages/IndividualOffer/IndividualOfferDescription/components/EanSearchCallout/EanSearchCallout'

import styles from './DetailsEanSearch.module.scss'

export type DetailsEanSearchProps = {
  shouldDisplayClearButton: boolean
  isProductBased: boolean
  initialEan?: string
  eanSubmitError?: string
  onEanSearch: (ean: string, product: Product) => void
  onEanClear: () => void
  isRequired: boolean
}

export const DetailsEanSearch = ({
  shouldDisplayClearButton,
  isProductBased,
  initialEan,
  eanSubmitError,
  onEanSearch,
  onEanClear,
  isRequired,
}: DetailsEanSearchProps): JSX.Element => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isClosed = withVenueHelpers(selectedPartnerVenue).isClosedOrClosing
  const [wasCleared, setWasCleared] = useState(false)

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
    resolver: yupResolver(generateEanSearchValidationSchema(isRequired)),
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

  const onSearch = async (data: EanSearchForm) => {
    if (data.eanSearch) {
      try {
        const product = await api.getProductByEan({
          path: {
            ean: data.eanSearch,
            offerer_id: selectedPartnerVenue.managingOfferer.id,
          },
        })
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

  const clearEan = () => {
    reset()
    onEanClear()
    setWasCleared(true)
  }

  const apiError = errors.eanSearch?.type === 'apiError'
  const shouldInputBeDisabled = isProductBased || isLoading || isClosed

  const shouldButtonBeDisabled =
    isProductBased || !ean || !isValid || !!apiError || isLoading

  return (
    <>
      <form onSubmit={handleSubmit(onSearch)}>
        <FormLayout fullWidthActions>
          <div className={styles['details-ean-search']}>
            <div>
              <TextInput
                label="Scanner ou rechercher un produit par EAN"
                error={errors.eanSearch?.message}
                disabled={shouldInputBeDisabled}
                required={isRequired}
                description="Format : EAN à 13 chiffres"
                {...(shouldDisplayClearButton
                  ? {
                      iconButton: {
                        icon: fullCloseIcon,
                        label: 'Effacer',
                        onClick: clearEan,
                        disabled: isLoading,
                      },
                    }
                  : {
                      icon: strokeBarcodeIcon,
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
        </FormLayout>
      </form>
      <output className={styles['details-ean-search-callout']}>
        {isProductBased && <EanSearchCallout />}
      </output>
    </>
  )
}
