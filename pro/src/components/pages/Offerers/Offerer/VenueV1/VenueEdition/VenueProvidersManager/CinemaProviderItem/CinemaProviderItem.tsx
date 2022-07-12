import * as pcapi from 'repository/pcapi/pcapi'

import React, { useCallback, useState } from 'react'
import { CinemaProviderFormDialog } from '../CinemaProviderFormDialog/CinemaProviderFormDialog'
import { IVenueProviderApi as VenueProvider } from './types'
import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'
import { showNotification } from 'store/reducers/notificationReducer'
import { useDispatch } from 'react-redux'

interface ICinemaProviderItemProps {
  afterVenueProviderEdit: (editedVenueProvider: VenueProvider) => void
  venueProvider: VenueProvider
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
      pcapi
        .editVenueProvider(payload)
        .then(editedVenueProvider => {
          // @ts-ignore
          afterVenueProviderEdit({ editedVenueProvider })
          dispatch(
            showNotification({
              text: 'Les modifications ont bien été importées et s’appliqueront aux nouvelles séances créées.',
              type: 'success',
            })
          )
        })
        .catch(error => {
          dispatch(
            showNotification({
              text: getRequestErrorStringFromErrors(error.errors),
              type: 'error',
            })
          )
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
