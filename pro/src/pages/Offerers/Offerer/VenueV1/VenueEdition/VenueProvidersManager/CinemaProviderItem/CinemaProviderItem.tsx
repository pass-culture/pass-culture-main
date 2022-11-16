import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'

import { CinemaProviderFormDialog } from '../CinemaProviderFormDialog/CinemaProviderFormDialog'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'
import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'

interface ICinemaProviderItemProps {
  afterVenueProviderEdit: ({
    editedVenueProvider,
  }: {
    editedVenueProvider: VenueProviderResponse
  }) => void
  venueProvider: VenueProviderResponse
  venueDepartementCode: string
}

export const CinemaProviderItem = ({
  afterVenueProviderEdit,
  venueProvider,
  venueDepartementCode,
}: ICinemaProviderItemProps) => {
  const [isOpenedFormDialog, setIsOpenedFormDialog] = useState(false)
  const notify = useNotification()
  const editVenueProvider = useCallback(
    (payload: any) => {
      api
        .updateVenueProvider(payload)
        .then(editedVenueProvider => {
          afterVenueProviderEdit({ editedVenueProvider })
          notify.success(
            'Les modifications ont bien été importées et s’appliqueront aux nouvelles séances créées.'
          )
        })
        .catch(error => {
          if (isErrorAPIError(error)) {
            notify.error(getRequestErrorStringFromErrors(getError(error)))
          }
        })
    },
    [afterVenueProviderEdit]
  )

  const openFormDialog = useCallback(() => {
    setIsOpenedFormDialog(true)
  }, [])

  const closeFromDialog = useCallback(() => {
    setIsOpenedFormDialog(false)
  }, [])

  const onConfirmDialog = useCallback(
    (payload: any) => {
      editVenueProvider(payload)

      closeFromDialog()
    },
    [closeFromDialog, editVenueProvider]
  )

  const initialValues = {
    isDuo: venueProvider.isDuo,
    isActive: venueProvider.isActive,
  }

  return (
    <VenueProviderItem
      venueDepartmentCode={venueDepartementCode}
      venueProvider={venueProvider}
    >
      <>
        <li>
          <span>{'Accepter les offres DUO : '}</span>
          <span>{`${venueProvider.isDuo ? 'Oui' : 'Non'} `}</span>
        </li>
        <button
          className="primary-button"
          onClick={openFormDialog}
          type="button"
        >
          Modifier les paramètres
        </button>
        {isOpenedFormDialog && (
          <CinemaProviderFormDialog
            onCancel={closeFromDialog}
            onConfirm={onConfirmDialog}
            initialValues={initialValues}
            providerId={venueProvider.providerId}
            venueId={venueProvider.venueId}
          />
        )}
      </>
    </VenueProviderItem>
  )
}
