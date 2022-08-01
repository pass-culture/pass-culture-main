import { Card } from '@material-ui/core'
import {
  Grid,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Typography,
} from '@mui/material'
import React from 'react'

import {
  EligibilitySubscriptionItem,
  SubscriptionItemStatus,
  SubscriptionItemType,
} from '../types'

import { BeneficiaryBadge } from './BeneficiaryBadge'
import { StatusAvatar } from './StatusAvatar'

type Props = {
  subscriptionItem: EligibilitySubscriptionItem
}

export const UserHistoryCard = ({ subscriptionItem }: Props) => {
  const cardStyle = {
    width: '100%',
    marginTop: '20px',
    padding: 30,
  }
  const gridStyle = { width: '100%', height: '100%', overflow: 'auto' }
  const beneficiaryBadge = <BeneficiaryBadge role={subscriptionItem.role} />

  return (
    <Card style={cardStyle}>
      <Typography variant={'h5'}>
        Parcours d'inscription
        <span style={{ marginLeft: '3rem' }}>{beneficiaryBadge}</span>
      </Typography>
      {subscriptionItem.items.length > 0 && (
        <Grid container spacing={5} sx={{ mt: 4 }} style={gridStyle}>
          <Grid item xs={6}>
            <List sx={{ width: '50%' }}>
              <ListItem>
                <ListItemText> Validation email</ListItemText>
                <ListItemAvatar>
                  <StatusAvatar
                    item={subscriptionItem.items.find(
                      subscriptionItem =>
                        subscriptionItem.type ===
                        SubscriptionItemType.EMAIL_VALIDATION
                    )}
                  />
                </ListItemAvatar>
              </ListItem>
              <ListItem>
                <ListItemText>Validation Téléphone</ListItemText>
                <ListItemAvatar>
                  <StatusAvatar
                    item={subscriptionItem.items.find(
                      (item: {
                        type: string
                        status: SubscriptionItemStatus
                      }) => item.type === SubscriptionItemType.PHONE_VALIDATION
                    )}
                  />
                </ListItemAvatar>
              </ListItem>
              <ListItem>
                <ListItemText>Profil Utilisateur</ListItemText>
                <ListItemAvatar>
                  <StatusAvatar
                    item={subscriptionItem.items.find(
                      item => item.type === SubscriptionItemType.USER_PROFILING
                    )}
                  />
                </ListItemAvatar>
              </ListItem>
            </List>
          </Grid>

          <Grid item xs={6}>
            <List sx={{ width: '50%' }}>
              <ListItem>
                <ListItemText>Complétion Profil</ListItemText>
                <ListItemAvatar>
                  <StatusAvatar
                    item={subscriptionItem.items.find(
                      (item: {
                        type: string
                        status: SubscriptionItemStatus
                      }) =>
                        item.type === SubscriptionItemType.PROFILE_COMPLETION
                    )}
                  />
                </ListItemAvatar>
              </ListItem>
              <ListItem>
                <ListItemText>ID Check</ListItemText>
                <ListItemAvatar>
                  <StatusAvatar
                    item={subscriptionItem.items.find(
                      item => item.type === SubscriptionItemType.IDENTITY_CHECK
                    )}
                  />
                </ListItemAvatar>
              </ListItem>
              <ListItem>
                <ListItemText>Honor Statement</ListItemText>
                <ListItemAvatar>
                  <StatusAvatar
                    item={subscriptionItem.items.find(
                      (item: {
                        type: string
                        status: SubscriptionItemStatus
                      }) => item.type === SubscriptionItemType.HONOR_STATEMENT
                    )}
                  />
                </ListItemAvatar>
              </ListItem>
            </List>
          </Grid>
        </Grid>
      )}
    </Card>
  )
}
