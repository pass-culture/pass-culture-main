import { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type { ListOffersOfferResponseModel } from '@/apiClient/v1'
import { GET_OFFERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { useQuerySearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { IndividualSearchFiltersParams } from '@/commons/core/Offers/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import {
  ModalImageUpsertOrEdit,
  type OnImageUploadArgs,
} from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { getStoredFilterConfig } from '@/components/OffersTableSearch/utils'
import strokeVisualArtIcon from '@/icons/stroke-visual-art.svg'
import { computeIndividualApiFilters } from '@/pages/IndividualOffers/utils/computeIndividualApiFilters'

type HeadlineOfferImageDialogsProps = {
  isFirstDialogOpen: boolean
  offer: ListOffersOfferResponseModel
  setIsFirstDialogOpen: (state: boolean) => void
}

export const HeadlineOfferImageDialogs = ({
  isFirstDialogOpen,
  setIsFirstDialogOpen,
  offer,
}: HeadlineOfferImageDialogsProps) => {
  const selectedOffererId = useAppSelector(ensureCurrentOfferer).id
  const { mutate } = useSWRConfig()

  const { headlineOffer, upsertHeadlineOffer } = useHeadlineOfferContext()
  const isReplacingHeadlineOffer = !!headlineOffer?.id

  const [isImageUploaderOpen, setIsImageUploaderOpen] = useState(false)
  const snackBar = useSnackBar()
  const { storedFilters } = getStoredFilterConfig('individual')
  const urlSearchFilters = useQuerySearchFilters()
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(storedFilters as Partial<IndividualSearchFiltersParams>),
  }

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedOffererId
  )

  const onImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    try {
      setIsImageUploaderOpen(false)

      const thumbnail = {
        thumb: imageFile,
        credit: credit ?? '',
        croppingRectHeight: cropParams?.height,
        croppingRectWidth: cropParams?.width,
        croppingRectX: cropParams?.x,
        croppingRectY: cropParams?.y,
        offerId: offer.id,
      }

      await mutate(
        [GET_OFFERS_QUERY_KEY, apiFilters],
        api.createThumbnail(thumbnail),
        {
          populateCache: (updatedThumbnail, offersList = []) => {
            return offersList.map((item: ListOffersOfferResponseModel) =>
              item.id === offer.id
                ? { ...item, thumbUrl: updatedThumbnail.url }
                : item
            )
          },
          revalidate: false,
        }
      )

      await upsertHeadlineOffer({
        offerId: offer.id,
        context: {
          actionType: isReplacingHeadlineOffer ? 'replace' : 'add',
          requiredImageUpload: true,
        },
      })
    } catch {
      snackBar.error(
        'Une erreur est survenue lors de la sauvegarde de votre image'
      )
    }
  }

  return (
    <>
      <ConfirmDialog
        icon={strokeVisualArtIcon}
        cancelText="Annuler"
        confirmText="Ajouter une image"
        onCancel={() => {
          setIsFirstDialogOpen(false)
        }}
        onConfirm={() => {
          setIsFirstDialogOpen(false)
          setIsImageUploaderOpen(true)
        }}
        title="Ajoutez une image pour mettre votre offre à la une"
        open={isFirstDialogOpen}
      />
      <ModalImageUpsertOrEdit
        mode={UploaderModeEnum.OFFER}
        onImageUpload={onImageUpload}
        open={isImageUploaderOpen}
        onOpenChange={() => setIsImageUploaderOpen(false)}
      />
    </>
  )
}
