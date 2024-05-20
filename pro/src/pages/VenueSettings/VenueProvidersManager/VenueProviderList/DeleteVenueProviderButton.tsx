import React, { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from 'config/swrQueryKeys'
import useNotification from 'hooks/useNotification'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { DeleteVenueProviderDialog } from './DeleteVenueProviderDialog'
import style from './VenueProviderItem.module.scss'

interface DeleteVenueProviderButtonProps {
  venueProviderId: number
  venue: GetVenueResponseModel
}

export const DeleteVenueProviderButton = ({
  venueProviderId,
  venue,
}: DeleteVenueProviderButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()
  const { mutate } = useSWRConfig()

  const tryToDeleteVenueProvider = async () => {
    setIsLoading(true)
    try {
      await api.deleteVenueProvider(venueProviderId)

      await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
    } catch (exception) {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard.'
      )
    } finally {
      setIsModalOpen(false)
      setIsLoading(false)
    }
  }

  return (
    <>
      <Button
        onClick={() => setIsModalOpen(true)}
        variant={ButtonVariant.TERNARY}
      >
        <SvgIcon
          src={fullTrashIcon}
          alt=""
          className={style['provider-action-icon']}
        />
        Supprimer
      </Button>

      {isModalOpen && (
        <DeleteVenueProviderDialog
          onConfirm={tryToDeleteVenueProvider}
          onCancel={() => setIsModalOpen(false)}
          isLoading={isLoading}
        />
      )}
    </>
  )
}
