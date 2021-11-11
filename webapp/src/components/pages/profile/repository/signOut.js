import unSetCustomUserId from '../../../../notifications/unSetCustomUserId'
import apiSignOut from './apiSignOut'

export const signOut = async () => {
  unSetCustomUserId()
  await apiSignOut()
}
