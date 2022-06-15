import * as React from 'react'
import { Logo } from './Logo'
import { Box, Typography, useMediaQuery, Theme } from '@mui/material'
import { AppBar, UserMenu } from 'react-admin'
import { Fragment } from 'react'
import { forwardRef } from 'react'
import { useLogout } from 'react-admin'
import ExitIcon from '@mui/icons-material/PowerSettingsNew'
import MenuItem from '@mui/material/MenuItem'

const MyLogoutButton = forwardRef((props, ref) => {
  const logout = useLogout()
  const handleClick = () => logout()
  return (
    <MenuItem onClick={handleClick}>
      <ExitIcon />
      &nbsp;Se&nbsp;Déconnecter
    </MenuItem>
  )
})

function CustomUserMenu() {
  return (
    <UserMenu>
      <MyLogoutButton />
    </UserMenu>
  )
}

export const CustomAppBar = (props: any) => {
  const isLargeEnough = useMediaQuery<Theme>(theme =>
    theme.breakpoints.up('sm')
  )
  return (
    <AppBar {...props} elevation={1} userMenu={<CustomUserMenu />}>
      <Typography
        variant="h6"
        color="inherit"
        sx={{
          flex: 1,
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
        }}
        id="react-admin-title"
      />
      {isLargeEnough && <Logo />}
      {isLargeEnough && <Fragment>&nbsp;Back Office</Fragment>}
      {isLargeEnough && <Box component="span" sx={{ flex: 1 }} />}
    </AppBar>
  )
}
