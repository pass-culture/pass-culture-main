import ExitIcon from '@mui/icons-material/PowerSettingsNew'
import { Box, Typography, useMediaQuery, Theme, MenuItem } from '@mui/material'
import React from 'react'
import { AppBar, useLogout, UserMenu } from 'react-admin'

import { Logo } from './Logo'

function MyLogoutButton() {
  const logout = useLogout()
  return (
    <MenuItem onClick={logout}>
      <ExitIcon />
      <span>Se Déconnecter</span>
    </MenuItem>
  )
}
function CustomUserMenu() {
  return (
    <UserMenu>
      <MyLogoutButton />
    </UserMenu>
  )
}

export const CustomAppBar = (props = {}) => {
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
      {isLargeEnough && <span>Back Office</span>}
      {isLargeEnough && <Box component="span" sx={{ flex: 1 }} />}
    </AppBar>
  )
}
