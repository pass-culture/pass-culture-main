import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { GET_OFFERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useQuerySearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import {
  OnImageUploadArgs,
  ModalImageEdit,
} from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import strokeStarIcon from 'icons/stroke-star.svg'
import strokeVisualArtIcon from 'icons/stroke-visual-art.svg'
import { useIndividualOffersContext } from 'pages/IndividualOffers/context/IndividualOffersContext'
import { computeIndividualApiFilters } from 'pages/IndividualOffers/utils/computeIndividualApiFilters'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

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
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const { mutate } = useSWRConfig()

  const { headlineOffer, upsertHeadlineOffer } = useIndividualOffersContext()
  const isReplacingHeadlineOffer = !!headlineOffer?.id

  const [isImageUploaderOpen, setIsImageUploaderOpen] = useState(false)
  const [isLastDialogOpen, setIsLastDialogOpen] = useState(false)
  const notify = useNotification()
  const isToggleAndMemorizeFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )
  const { storedFilters } = getStoredFilterConfig('individual')
  const urlSearchFilters = useQuerySearchFilters()
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(isToggleAndMemorizeFiltersEnabled
      ? (storedFilters as Partial<SearchFiltersParams>)
      : {}),
  }

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedOffererId?.toString()
  )

  const onImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    try {
      setIsImageUploaderOpen(false)

      await mutate(
        [GET_OFFERS_QUERY_KEY, apiFilters],
        api.createThumbnail({
          // TODO This TS error will be removed when spectree is updated to the latest
          // version (dependant on Flask update) which will include files in the generated schema
          // @ts-expect-error
          thumb: imageFile,
          credit: credit ?? '',
          croppingRectHeight: cropParams?.height,
          croppingRectWidth: cropParams?.width,
          croppingRectX: cropParams?.x,
          croppingRectY: cropParams?.y,
          offerId: offer.id,
        }),
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
      setIsLastDialogOpen(true)
    } catch {
      notify.error(
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
      <DialogBuilder
        open={isImageUploaderOpen}
        onOpenChange={() => setIsImageUploaderOpen(false)}
      >
        <ModalImageEdit
          mode={UploaderModeEnum.OFFER}
          onImageUpload={onImageUpload}
        />
      </DialogBuilder>
      <ConfirmDialog
        icon={strokeStarIcon}
        cancelText="Annuler"
        confirmText="Confirmer"
        onCancel={() => {
          setIsLastDialogOpen(false)
        }}
        onConfirm={async () => {
          await upsertHeadlineOffer({
            offerId: offer.id,
            context: {
              actionType: isReplacingHeadlineOffer ? 'replace' : 'add',
              requiredImageUpload: true,
            },
          })
          setIsLastDialogOpen(false)
        }}
        title="Votre offre va être mise à la une !"
        open={isLastDialogOpen}
      />
    </>
  )
}
