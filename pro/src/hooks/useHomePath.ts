import useCurrentUser from 'hooks/useCurrentUser'

const useHomePath = () => {
  const { currentUser } = useCurrentUser()
  const { isAdmin } = currentUser || {}
  return isAdmin ? '/structures' : '/accueil'
}

export default useHomePath
