import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { isOfferAllocineSynchronized } from 'commons/core/Offers/utils/typology'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { isEqual } from 'commons/utils/isEqual'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import { DuoCheckbox } from 'components/DuoCheckbox/DuoCheckbox'
import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  UNIQUE_PRICE,
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
  INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_MAX_LENGTH,
} from 'components/IndividualOffer/PriceCategoriesScreen/form/constants'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { PriceInput } from 'ui-kit/formV2/PriceInput/PriceInput'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { getSuccessMessage } from '../utils/getSuccessMessage'

import { computeInitialValues } from './form/computeInitialValues'
import { submitToApi } from './form/submitToApi'
import { PriceCategoriesFormValues, PriceCategoryForm } from './form/types'
import styles from './PriceCategoriesScreen.module.scss'

export interface PriceCategoriesScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

const hasFieldChange = (
  priceCategories: PriceCategoryForm[],
  initialPriceCategories: Record<string, Partial<PriceCategoryForm>>,
  field: keyof PriceCategoryForm
) =>
  priceCategories.some((priceCategory) => {
    // if no id, it is new and has no stocks
    if (!priceCategory.id) {
      return false
    }
    // have fields which trigger warning been edited ?
    const initialpriceCategory = initialPriceCategories[priceCategory.id]
    return initialpriceCategory[field] !== priceCategory[field]
  })

/**
 * @function arePriceCategoriesChanged
 * Returns `true` if at least one of the initial price categories has changed
 * and `false` otherwise (even if there are additional price cateogires in the values).
 * */
export const arePriceCategoriesChanged = (
  initialValues: PriceCategoriesFormValues,
  values: PriceCategoriesFormValues
): boolean => {
  const initialPriceCategories: Record<
    string,
    Partial<PriceCategoryForm>
  > = initialValues.priceCategories.reduce(
    (dict: Record<string, Partial<PriceCategoryForm>>, priceCategory) => {
      dict[priceCategory.id || 'new'] = {
        id: priceCategory.id,
        label: priceCategory.label,
        price: priceCategory.price,
      }
      return dict
    },
    {}
  )

  const changedPriceCategories = values.priceCategories.filter(
    (priceCategory) => {
      if (!priceCategory.id) {
        return false
      }
      if (
        priceCategory.price !==
          initialPriceCategories[priceCategory.id].price ||
        priceCategory.label !== initialPriceCategories[priceCategory.id].label
      ) {
        return true
      }
      return false
    }
  )

  return hasFieldChange(changedPriceCategories, initialPriceCategories, 'price')
}

export const PriceCategoriesScreen = ({
  offer,
}: PriceCategoriesScreenProps): JSX.Element => {
  const { subCategories } = useIndividualOfferContext()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const mode = useOfferWizardMode()
  const notify = useNotification()
  const { mutate } = useSWRConfig()
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] =
    useState<boolean>(false)

  const isDisabledBySynchronization =
    Boolean(offer.lastProvider) && !isOfferAllocineSynchronized(offer)
  const isDisabled =
    isOfferDisabled(offer.status) || isDisabledBySynchronization
  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const defaultValues = computeInitialValues(offer)
  const hookForm = useForm({
    defaultValues,
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    getValues,
    setValue,
    reset,
    watch,
    control,
    formState: { isDirty, isSubmitting },
  } = hookForm

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'priceCategories',
  })

  const priceCategories = watch('priceCategories')

  const onSubmit = async () => {
    const values = getValues()
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.TARIFS
          : OFFER_WIZARD_STEP_IDS.STOCKS,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
      isOnboarding,
    })

    // Return when saving in edition with no change and no addition to the list of price categories
    const isFormEmpty = isEqual(defaultValues, values)

    if (isFormEmpty && mode === OFFER_WIZARD_MODE.EDITION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Show popin if necessary
    const showConfirmationModal =
      offer.hasStocks && arePriceCategoriesChanged(defaultValues, values)
    setIsConfirmationModalOpen(showConfirmationModal)
    if (!isConfirmationModalOpen && showConfirmationModal) {
      return
    }

    // Submit
    try {
      await submitToApi(values, offer, reset)
      await mutate([GET_OFFER_QUERY_KEY, offer.id])
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error.message)
      }
      return
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(nextStepUrl)
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(getSuccessMessage(mode))
    }
    setIsConfirmationModalOpen(false)
  }

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode,
          isOnboarding,
        })
      )
    }
  }

  const [currentDeletionIndex, setCurrentDeletionIndex] = useState<
    number | null
  >(null)

  const onDeletePriceCategory = async (
    index: number,
    priceCategories: PriceCategoryForm[]
  ) => {
    const priceCategoryId = priceCategories[index].id

    if (priceCategoryId) {
      if (currentDeletionIndex === null && offer.hasStocks) {
        setCurrentDeletionIndex(index)
        return
      } else {
        setCurrentDeletionIndex(null)
      }
      try {
        await api.deletePriceCategory(offer.id, priceCategoryId)
        remove(index)
        notify.success('Le tarif a été supprimé.')
      } catch {
        notify.error(
          'Une erreur est survenue lors de la suppression de votre tarif'
        )
      }
    } else {
      remove(index)
    }

    if (priceCategories.length === 2) {
      setValue(`priceCategories.0.label`, UNIQUE_PRICE)
      const otherPriceCategory = priceCategories.filter(
        (pC) => pC.id !== priceCategoryId
      )
      const otherPriceCategoryId = otherPriceCategory[0]?.id
      if (otherPriceCategoryId) {
        const requestBody = {
          priceCategories: [
            {
              label: UNIQUE_PRICE,
              id: otherPriceCategoryId,
            },
          ],
        }
        try {
          await api.postPriceCategories(offer.id, requestBody)
        } catch {
          notify.error(
            'Une erreur est survenue lors de la mise à jour de votre tarif'
          )
        }
      }
    }
  }

  return (
    <>
      <ConfirmDialog
        onCancel={() => setIsConfirmationModalOpen(false)}
        onConfirm={handleSubmit(onSubmit)}
        title="Cette modification de tarif s’appliquera à l’ensemble des dates qui y sont associées."
        confirmText="Confirmer la modification"
        cancelText="Annuler"
        open={isConfirmationModalOpen}
      >
        {(offer.bookingsCount ?? 0) > 0 && (
          <>
            Le tarif restera inchangé pour les personnes ayant déjà réservé
            cette offre.
          </>
        )}
      </ConfirmDialog>

      <form onSubmit={handleSubmit(onSubmit)}>
        <>
          <FormLayout>
            <FormLayout.MandatoryInfo areAllFieldsMandatory />
            <FormLayout.Section title="Tarifs">
              <ConfirmDialog
                onCancel={() => setCurrentDeletionIndex(null)}
                onConfirm={() => {
                  return onDeletePriceCategory(
                    //  TODO : restructure this composant so that this hack is not necessary
                    //  By creating a component for each of the price category lines
                    currentDeletionIndex!,
                    priceCategories
                  )
                }}
                title="En supprimant ce tarif vous allez aussi supprimer l’ensemble des dates qui lui sont associées."
                confirmText="Confirmer la supression"
                cancelText="Annuler"
                open={currentDeletionIndex !== null}
              />
              {fields.map((field, index) => (
                <fieldset
                  key={field.id}
                  data-testid={`priceCategories.${index}.label`}
                >
                  <legend className={styles['visually-hidden']}>
                    Tarif {index + 1}
                  </legend>
                  <FormLayout.Row
                    inline
                    smSpaceAfter
                    className={styles['form-layout-row-price-category']}
                  >
                    <TextInput
                      {...register(`priceCategories.${index}.label`)}
                      name={`priceCategories.${index}.label`}
                      label="Intitulé du tarif"
                      description="Par exemple : catégorie 2, moins de 18 ans, pass 3 jours..."
                      maxLength={PRICE_CATEGORY_LABEL_MAX_LENGTH}
                      count={field.price.toString().length}
                      className={styles['label-input']}
                      labelClassName={styles['label-input-label']}
                      disabled={priceCategories.length <= 1 || isDisabled}
                    />
                    <PriceInput
                      {...register(`priceCategories.${index}.price`)}
                      className={styles['price-input']}
                      name={`priceCategories.${index}.price`}
                      label="Prix par personne"
                      max={PRICE_CATEGORY_PRICE_MAX}
                      rightIcon={strokeEuroIcon}
                      disabled={isDisabled}
                      showFreeCheckbox
                      hideAsterisk={true}
                      smallLabel
                      updatePriceValue={(value) =>
                        setValue(
                          `priceCategories.${index}.price`,
                          parseFloat(value)
                        )
                      }
                    />
                    {mode === OFFER_WIZARD_MODE.CREATION && (
                      <Button
                        className={styles['delete-icon']}
                        iconClassName={styles['delete-icon-svg']}
                        data-testid={'delete-button'}
                        variant={ButtonVariant.TERNARY}
                        icon={fullTrashIcon}
                        iconPosition={IconPositionEnum.CENTER}
                        disabled={priceCategories.length <= 1 || isDisabled}
                        onClick={() =>
                          onDeletePriceCategory(index, priceCategories)
                        }
                        tooltipContent={
                          priceCategories.length > 1 && !isDisabled ? (
                            <>Supprimer le tarif</>
                          ) : undefined
                        }
                      />
                    )}
                  </FormLayout.Row>
                </fieldset>
              ))}

              <Button
                variant={ButtonVariant.TERNARY}
                icon={fullMoreIcon}
                onClick={() => {
                  append(INITIAL_PRICE_CATEGORY)
                  if (priceCategories[0].label === UNIQUE_PRICE) {
                    setValue(`priceCategories.0.label`, '')
                  }
                }}
                disabled={
                  priceCategories.length >= PRICE_CATEGORY_MAX_LENGTH ||
                  isDisabled
                }
              >
                Ajouter un tarif
              </Button>
            </FormLayout.Section>
          </FormLayout>

          {canBeDuo && (
            <FormLayout fullWidthActions>
              <FormLayout.Section
                className={styles['duo-section']}
                title="Réservations “Duo”"
              >
                <DuoCheckbox
                  {...register('isDuo')}
                  checked={Boolean(watch('isDuo'))}
                  disabled={isDisabled}
                />
              </FormLayout.Section>
            </FormLayout>
          )}
        </>

        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.TARIFS}
          isDisabled={isSubmitting}
          dirtyForm={isDirty}
        />
      </form>

      <RouteLeavingGuardIndividualOffer when={isDirty && !isSubmitting} />
    </>
  )
}
