import { FormikProvider, Form, useFormik } from 'formik'
import { useState, useRef, useEffect } from 'react'
import { useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { isErrorAPIError, getError } from 'apiClient/helpers'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeBarcode from 'icons/stroke-barcode.svg'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Button } from 'ui-kit/Button/Button'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { EanSearchCallout } from '../EanSearchCallout/EanSearchCallout'
import { Product } from '../types'
import { isSubCategoryCDOrVinyl } from '../utils'
import { eanSearchValidationSchema } from '../validationSchema'

import styles from './DetailsEanSearch.module.scss'

export type DetailsEanSearchProps = {
  productId: string
  subcategoryId: string
  isOfferProductBased: boolean
  onEanSearch: (ean: string, product: Product) => Promise<void>
  resetForm: () => void
}

export const DetailsEanSearch = ({
  productId,
  subcategoryId,
  isOfferProductBased,
  onEanSearch,
  resetForm,
}: DetailsEanSearchProps): JSX.Element => {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const inputRef = useRef<HTMLInputElement>(null)
  const [isFetchingProduct, setIsFetchingProduct] = useState(false)
  const [subcatError, setSubcatError] = useState<string | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [wasCleared, setWasCleared] = useState(false)

  const isNotAnOfferYetButProductBased = !isOfferProductBased && !!productId
  const isProductBased = isOfferProductBased || isNotAnOfferYetButProductBased

  const formik = useFormik({
    initialValues: { eanSearch: '' },
    validationSchema: eanSearchValidationSchema,
    onSubmit: () => undefined,
  })

  const ean = formik.values.eanSearch
  const formikError = formik.errors.eanSearch

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

  const onSearch = async () => {
    console.log('onSearch', ean)
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
        setApiError(errorMessage)
      }
    }
  }

  const onEanClear = () => {
    console.log('onEanClear')
    resetForm()
    setWasCleared(true)
  }

  const shouldInputBeDisabled = isProductBased || isFetchingProduct
  const shouldInputBeRequired = !!subcatError
  const shouldButtonBeDisabled =
    isProductBased || !ean || !!formikError || !!apiError || isFetchingProduct
  const displayClearButton = isNotAnOfferYetButProductBased

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
                  isDirtyDraftOfferProductBased={isNotAnOfferYetButProductBased}
                />
              )}
            </div>
          </div>
        </FormLayout>
      </Form>
    </FormikProvider>
  )
}
