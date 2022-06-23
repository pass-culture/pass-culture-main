import ExitIcon from '@mui/icons-material/PowerSettingsNew'
import { Box, useMediaQuery, Theme, MenuItem, Stack } from '@mui/material'
import React from 'react'
import { AppBar, useLogout, UserMenu } from 'react-admin'

import { Colors } from './Colors'
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
    theme.breakpoints.up('md')
  )
  return (
    <AppBar {...props} elevation={1} userMenu={<CustomUserMenu />}>
      <Stack direction={'row'} sx={{ mx: 'auto', pl: '12rem' }}>
        {isLargeEnough && <Logo fill={Colors.WHITE} />}
        {isLargeEnough && <span>Back Office</span>}
        {isLargeEnough && <Box component="span" sx={{ flex: 1 }} />}
      </Stack>
    </AppBar>
  )
}
