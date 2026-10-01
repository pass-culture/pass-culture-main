import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { getError, isErrorAPIError } from '@/apiClient/helpers'
import type { GetProductInformations } from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullCloseIcon from '@/icons/full-close.svg'
import strokeBarcodeIcon from '@/icons/stroke-barcode.svg'
import {
  type EanSearchForm,
  generateEanSearchValidationSchema,
} from '@/pages/IndividualOffer/IndividualOfferDescription/commons/validationSchema'
import { EanSearchCallout } from '@/pages/IndividualOffer/IndividualOfferDescription/components/EanSearchCallout/EanSearchCallout'

import styles from './DetailsEanSearch.module.scss'

export type DetailsEanSearchProps = {
  required: boolean
  disabled: boolean
  productEan: GetProductInformations['ean']
  onProductChange: (product: GetProductInformations | null) => void
  canClearProduct: boolean
}

export const DetailsEanSearch = ({
  productEan,
  onProductChange,
  canClearProduct,
  required,
  disabled,
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
    defaultValues: { eanSearch: productEan || '' },
    resolver: yupResolver(generateEanSearchValidationSchema(required)),
    mode: 'onChange',
  })

  const ean = watch('eanSearch', '')

  useEffect(() => {
    if (wasCleared) {
      setFocus('eanSearch')
      setWasCleared(false)
    }
  }, [wasCleared, setFocus])

  const onSearch = async (data: EanSearchForm) => {
    if (data.eanSearch) {
      try {
        const product = await api.getProductByEan({
          path: {
            ean: data.eanSearch,
            offerer_id: selectedPartnerVenue.managingOfferer.id,
          },
        })
        onProductChange({ ...product, ean: data.eanSearch })
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
    onProductChange(null)
    setWasCleared(true)
  }

  const apiError = errors.eanSearch?.type === 'apiError'
  const shouldInputBeDisabled = disabled || isLoading || isClosed
  const shouldButtonBeDisabled =
    disabled || !ean || !isValid || !!apiError || isLoading

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
                required={required}
                description="Format : EAN à 13 chiffres"
                {...(canClearProduct && productEan
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
        {productEan && <EanSearchCallout />}
      </output>
    </>
  )
}
