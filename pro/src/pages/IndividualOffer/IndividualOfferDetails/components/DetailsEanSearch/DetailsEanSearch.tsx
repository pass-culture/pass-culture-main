import { FormikProvider, Form, useFormik } from 'formik'
import { useState, useRef, useEffect } from 'react'
import { useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { isErrorAPIError, getError } from 'apiClient/helpers'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeBarcode from 'icons/stroke-barcode.svg'
import { Product } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { eanSearchValidationSchema } from 'pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'
import { EanSearchCallout } from 'pages/IndividualOffer/IndividualOfferDetails/components/EanSearchCallout/EanSearchCallout'
import { Button } from 'ui-kit/Button/Button'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './DetailsEanSearch.module.scss'

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
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const inputRef = useRef<HTMLInputElement>(null)
  const [isFetchingProduct, setIsFetchingProduct] = useState(false)
  const [subcatError, setSubcatError] = useState<string | null>(null)
  const [productApiError, setProductApiError] = useState<string | null>(null)
  const [wasCleared, setWasCleared] = useState(false)

  const isProductBased = !!productId
  const isDirtyDraftOfferProductBased = isDirtyDraftOffer && isProductBased
  const isDirtyDraftOfferNotProductBased = isDirtyDraftOffer && !isProductBased

  const formik = useFormik({
    initialValues: { eanSearch: initialEan || '' },
    validationSchema: eanSearchValidationSchema,
    onSubmit: () => undefined,
  })

  const ean = formik.values.eanSearch
  const formikError = formik.errors.eanSearch

  useEffect(() => {
    setProductApiError(null)
  }, [ean])

  useEffect(() => {
    if (wasCleared && inputRef.current) {
      inputRef.current.focus()
      setWasCleared(false)
    }
  }, [wasCleared, productId])

  useEffect(() => {
    if (isDirtyDraftOfferNotProductBased && isSubCategoryCD(subcategoryId)) {
      setSubcatError('Les offres de type CD doivent être liées à un produit.')
    } else {
      setSubcatError(null)
    }
  }, [isDirtyDraftOfferNotProductBased, subcategoryId])

  const onSearch = async () => {
    if (ean) {
      try {
        setIsFetchingProduct(true)

        if (!selectedOffererId) {
          throw new Error('Offerer should have already been selected')
        }

        const product = await api.getProductByEan(ean, selectedOffererId)
        await onEanSearch(ean, product)

        setIsFetchingProduct(false)
      } catch (err) {
        const fallbackMessage = 'Une erreur est survenue lors de la recherche'
        const errorMessage = isErrorAPIError(err)
          ? getError(err).ean?.[0] || fallbackMessage
          : fallbackMessage
        setIsFetchingProduct(false)
        setProductApiError(errorMessage)
      }
    }
  }

  const onEanClear = () => {
    formik.resetForm()
    onEanReset()
    setWasCleared(true)
  }

  const apiError = eanSubmitError || productApiError

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
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
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
                type="submit"
                className={styles['details-ean-search-button']}
                disabled={shouldButtonBeDisabled}
                onClick={onSearch}
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
      </Form>
    </FormikProvider>
  )
}
