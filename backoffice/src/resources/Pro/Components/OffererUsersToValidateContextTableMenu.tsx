import MoreVertIcon from '@mui/icons-material/MoreVert'
import { IconButton, Menu, MenuItem } from '@mui/material'
import React, { useState } from 'react'
import { useNotify } from 'react-admin'

import {
  getGenericHttpErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../../providers/apiHelpers'
import { apiProvider } from '../../../providers/apiProvider'

import { RejectUserOffererModal } from './RejectUserOffererModal'
import { SetPendingUserOffererModal } from './SetPendingUserOffererModal'

type Props = {
  id: number
}

export const OffererUserssToValidateContextTableMenu = ({ id }: Props) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  const open = Boolean(anchorEl)
  const notify = useNotify()
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }
  const handleClose = () => {
    setAnchorEl(null)
  }
  return (
    <>
      <IconButton
        aria-label={'more'}
        id={'long-button' + id}
        aria-controls={open ? 'long-menu' : undefined}
        aria-expanded={open ? 'true' : undefined}
        aria-haspopup="true"
        onClick={handleClick}
        color={'error'}
      >
        <MoreVertIcon />
      </IconButton>
      <Menu
        id="long-menu"
        MenuListProps={{
          'aria-labelledby': 'long-button',
        }}
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
      >
        <MenuItem
          key="valider"
          onClick={async () => {
            try {
              await apiProvider().validateOffererAttachment({
                userOffererId: id,
              })
              notify('Le rattachement a été validé avec succès !', {
                type: 'success',
              })
              handleClose()
            } catch (error) {
              if (error instanceof PcApiHttpError) {
                notify(getHttpApiErrorMessage(error), { type: 'error' })
              } else {
                notify(await getGenericHttpErrorMessage(error as Response), {
                  type: 'error',
                })
              }
              handleClose()
            }
          }}
        >
          Valider
        </MenuItem>
        <RejectUserOffererModal userOffererId={id} />
        <SetPendingUserOffererModal userOffererId={id} />
      </Menu>
    </>
  )
}
