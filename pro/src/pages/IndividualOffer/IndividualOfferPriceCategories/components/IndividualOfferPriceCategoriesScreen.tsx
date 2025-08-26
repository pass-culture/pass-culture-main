import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useState } from 'react'
import { useFieldArray, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferAllocineSynchronized } from '@/commons/core/Offers/utils/typology'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { convertPacificFrancToEuro } from '@/commons/utils/convertEuroToPacificFranc'
import { isEqual } from '@/commons/utils/isEqual'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { DuoCheckbox } from '@/components/DuoCheckbox/DuoCheckbox'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeFrancIcon from '@/icons/stroke-franc.svg'
import { getSuccessMessage } from '@/pages/IndividualOffer/commons/getSuccessMessage'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'
import { PriceInput } from '@/ui-kit/form/PriceInput/PriceInput'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import { arePriceCategoriesChanged } from '../commons/arePriceCategoriesChanged'
import { computeInitialValues } from '../commons/computeInitialValues'
import {
  INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_MAX_LENGTH,
  UNIQUE_PRICE,
} from '../commons/constants'
import { submitToApi } from '../commons/submitToApi'
import type {
  PriceCategoriesFormValues,
  PriceCategoryForm,
} from '../commons/types'
import { getValidationSchema } from '../commons/validationSchema'
import styles from './IndividualOfferPricesScreen.module.scss'

export interface IndividualOfferPriceCategoriesScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

export const IndividualOfferPriceCategoriesScreen = ({
  offer,
}: IndividualOfferPriceCategoriesScreenProps): JSX.Element => {
  const { subCategories } = useIndividualOfferContext()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const mode = useOfferWizardMode()
  const notify = useNotification()
  const { mutate } = useSWRConfig()
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] =
    useState<boolean>(false)

  const isCaledonian = useIsCaledonian()

  const isMediaPageEnabled = useActiveFeature('WIP_ADD_VIDEO')

  const isDisabledBySynchronization =
    Boolean(offer.lastProvider) && !isOfferAllocineSynchronized(offer)
  const isDisabled =
    isOfferDisabled(offer.status) || isDisabledBySynchronization
  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const defaultValues = computeInitialValues(offer, isCaledonian)
  const hookForm = useForm<PriceCategoriesFormValues>({
    defaultValues,
    resolver: yupResolver<PriceCategoriesFormValues, unknown, unknown>(
      getValidationSchema(isCaledonian)
    ),
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    getValues,
    setValue,
    watch,
    control,
    formState: { errors, isDirty, isSubmitting },
  } = hookForm

  useEffect(() => {
    const newValues = computeInitialValues(offer, isCaledonian)
    hookForm.reset(newValues)
  }, [isCaledonian, offer])

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'priceCategories',
  })

  const priceCategories = watch('priceCategories')

  const onSubmit = async () => {
    let values = { ...getValues(), isDuo: getValues().isDuo }

    if (isCaledonian) {
      values = {
        ...values,
        priceCategories: values.priceCategories.map((cat) => ({
          ...cat,
          price: convertPacificFrancToEuro(Number(cat.price)),
        })),
      }
    }

    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
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
      await submitToApi(values, offer)
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
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: isMediaPageEnabled
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
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
    const hasOnlyTwo = priceCategories.length === 2

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

    if (hasOnlyTwo) {
      setValue(`priceCategories.0.label`, UNIQUE_PRICE, {
        shouldValidate: true,
      })

      const remaining = priceCategories.filter(
        (pC) => pC.id !== priceCategoryId
      )

      if (remaining[0]?.id) {
        const requestBody = {
          priceCategories: [
            {
              label: UNIQUE_PRICE,
              id: remaining[0]?.id,
            },
          ],
        }

        try {
          await api.postPriceCategories(offer.id, requestBody)
        } catch {
          notify.error(
            'Une erreur est survenue lors de la suppression de votre tarif'
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
        {(offer.bookingsCount ?? 0) > 0 &&
          'Le tarif restera inchangé pour les personnes ayant déjà réservé cette offre.'}
      </ConfirmDialog>
      <form onSubmit={handleSubmit(onSubmit)}>
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
              confirmText="Confirmer la suppression"
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
                  mdSpaceAfter
                  className={styles['form-layout-row-price-category']}
                >
                  <TextInput
                    {...register(`priceCategories.${index}.label`)}
                    name={`priceCategories.${index}.label`}
                    label="Intitulé du tarif"
                    description="Par exemple : catégorie 2, moins de 18 ans, pass 3 jours..."
                    maxLength={PRICE_CATEGORY_LABEL_MAX_LENGTH}
                    count={priceCategories[index]?.label.length}
                    className={styles['label-input']}
                    labelClassName={styles['label-input-label']}
                    disabled={priceCategories.length <= 1 || isDisabled}
                    error={errors.priceCategories?.[index]?.label?.message}
                    autoComplete="off"
                  />
                  <PriceInput
                    {...register(`priceCategories.${index}.price`)}
                    className={styles['price-input']}
                    name={`priceCategories.${index}.price`}
                    label="Prix par personne"
                    rightIcon={isCaledonian ? strokeFrancIcon : strokeEuroIcon}
                    disabled={isDisabled}
                    showFreeCheckbox
                    hideAsterisk={true}
                    smallLabel
                    updatePriceValue={(value) =>
                      setValue(
                        `priceCategories.${index}.price`,
                        isCaledonian ? Number(value) : parseFloat(value),
                        { shouldValidate: true }
                      )
                    }
                    error={errors.priceCategories?.[index]?.price?.message}
                  />

                  {mode === OFFER_WIZARD_MODE.CREATION && (
                    <Button
                      aria-label={`Supprimer le tarif ${priceCategories[index].label}`}
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
                        priceCategories.length > 1 && !isDisabled
                          ? 'Supprimer le tarif'
                          : undefined
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
                  setValue(`priceCategories.0.label`, '', {
                    shouldValidate: true,
                  })
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
        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS}
          isDisabled={isSubmitting}
          dirtyForm={isDirty}
          isEvent={offer.isEvent}
        />
      </form>
      <RouteLeavingGuardIndividualOffer when={isDirty && !isSubmitting} />
    </>
  )
}
