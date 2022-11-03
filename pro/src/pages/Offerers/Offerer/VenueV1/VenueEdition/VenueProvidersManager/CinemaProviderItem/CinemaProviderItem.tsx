import React, { useCallback, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { VenueProviderResponse } from 'apiClient/v1'
import { showNotification } from 'store/reducers/notificationReducer'

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
  const dispatch = useDispatch()
  const editVenueProvider = useCallback(
    (payload: any) => {
      api
        .updateVenueProvider(payload)
        .then(editedVenueProvider => {
          afterVenueProviderEdit({ editedVenueProvider })
          dispatch(
            showNotification({
              text: 'Les modifications ont bien été importées et s’appliqueront aux nouvelles séances créées.',
              type: 'success',
            })
          )
        })
        .catch(error => {
          if (isErrorAPIError(error)) {
            dispatch(
              showNotification({
                text: getRequestErrorStringFromErrors(getError(error)),
                type: 'error',
              })
            )
          }
        })
    },
    [afterVenueProviderEdit, dispatch]
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
