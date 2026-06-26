import { useEffect, useState } from 'react'
import { useFormContext } from 'react-hook-form'

import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
  type GetEducationalOffererResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  isCollectiveOffer,
  Mode,
  type OfferEducationalFormValues,
} from '@/commons/core/OfferEducational/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from '@/components/BannerPublicApi/BannerPublicApi'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import type { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import type { DomainOption } from '../useOfferEducationalFormData'
import { FormAccessibility } from './FormAccessibility/FormAccessibility'
import { FormContact } from './FormContact/FormContact'
import { FormContactTemplate } from './FormContactTemplate/FormContactTemplate'
import { FormDates } from './FormDates/FormDates'
import {
  FormImageUploader,
  type ImageUploaderOfferProps,
} from './FormImageUploader/FormImageUploader'
import { FormLocation } from './FormLocation/FormLocation'
import { FormNotifications } from './FormNotifications/FormNotifications'
import { FormOfferType } from './FormOfferType/FormOfferType'
import { FormParticipants } from './FormParticipants/FormParticipants'
import styles from './OfferEducationalForm.module.scss'

export type OfferEducationalFormProps = {
  userOfferer: GetEducationalOffererResponseModel | null
  domainsOptions: DomainOption[]
  isTemplate: boolean
  mode: Mode
  imageOffer: ImageUploaderOfferProps['imageOffer']
  onImageUpload: ImageUploaderOfferProps['onImageUpload']
  onImageDelete: ImageUploaderOfferProps['onImageDelete']
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  isSubmitting: boolean
}

export const OfferEducationalForm = ({
  userOfferer,
  mode,
  domainsOptions,
  isTemplate,
  imageOffer,
  onImageUpload,
  onImageDelete,
  offer,
  isSubmitting,
}: OfferEducationalFormProps): JSX.Element => {
  const [isEligible, setIsEligible] = useState<boolean>()
  const { logEvent } = useAnalytics()

  const { formState, watch, setValue } =
    useFormContext<OfferEducationalFormValues>()

  const canEditDetails =
    !offer ||
    isActionAllowedOnCollectiveOffer(
      offer,
      isCollectiveOffer(offer)
        ? CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
        : CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS
    )

  useEffect(() => {
    if (userOfferer) {
      if (mode === Mode.EDITION || mode === Mode.READ_ONLY) {
        setIsEligible(true)
      } else {
        setIsEligible(userOfferer.allowedOnAdage)
      }
    } else {
      setIsEligible(false)
    }
  }, [userOfferer, mode])

  const logOnImageDropOrSelected = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.OFFER_COLLECTIVE,
      imageCreationStage: 'add image',
    })
  }

  const handleImageUpload = (image: OnImageUploadArgs) => {
    onImageUpload(image)
    setValue('imageUrl', image.imageCroppedDataUrl, { shouldDirty: true })
    setValue('imageCredit', image.credit ?? undefined, { shouldDirty: true })
  }

  const handleImageDelete = () => {
    onImageDelete()
    setValue('imageUrl', undefined, { shouldDirty: true })
    setValue('imageCredit', undefined, { shouldDirty: true })
  }

  return (
    <>
      <ScrollToFirstHookFormErrorAfterSubmit />
      <FormLayout fullWidthActions>
        {isCollectiveOffer(offer) && offer.isPublicApi && (
          <BannerPublicApi className={styles['banner-space']} />
        )}
        {!userOfferer?.allowedOnAdage ? (
          <Banner
            title="Validation requise"
            description="La création d'offres collectives nécessite la validation de votre entité juridique."
          />
        ) : (
          <>
            <FormLayout.MandatoryInfo />
            {watch('offererId') && watch('venueId') && isEligible ? (
              <>
                <FormOfferType
                  domainsOptions={domainsOptions}
                  disableForm={!canEditDetails}
                  isTemplate={isTemplate}
                />
                <FormImageUploader
                  onImageDelete={handleImageDelete}
                  onImageUpload={handleImageUpload}
                  onImageDropOrSelected={logOnImageDropOrSelected}
                  imageOffer={imageOffer}
                  disableForm={!canEditDetails}
                  isTemplate={isTemplate}
                />
                {isTemplate && (
                  <FormDates
                    disableForm={!canEditDetails}
                    dateCreated={offer?.dateCreated}
                  />
                )}

                <FormLocation disableForm={!canEditDetails} />

                <FormParticipants disableForm={!canEditDetails} />
                <FormAccessibility disableForm={!canEditDetails} />
                {isTemplate ? (
                  <FormContactTemplate disableForm={!canEditDetails} />
                ) : (
                  <FormContact disableForm={!canEditDetails} />
                )}
                <FormNotifications disableForm={!canEditDetails} />
              </>
            ) : null}
          </>
        )}
      </FormLayout>
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            to={computeCollectiveOffersUrl({})}
            label="Annuler et quitter"
          />
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right
          dirtyForm={formState.isDirty || !offer}
          mode={mode}
        >
          <Button
            type="submit"
            disabled={
              !isEligible ||
              !canEditDetails ||
              isSubmitting ||
              (!formState.isDirty && mode === Mode.EDITION)
            }
            label="Enregistrer et continuer"
          />
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
