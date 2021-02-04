import { createSelector } from 'reselect'

export const isWalletValid = createSelector(
  state => state.currentUser.deposit_expiration_date,
  deposit_expiration_date => {
    if (deposit_expiration_date == null) {
      return false
    }

    return new Date(deposit_expiration_date) > Date.now()
  }
)
