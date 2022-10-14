import useCurrentUser from 'hooks/useCurrentUser'

const useHomePath = () => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  return isAdmin ? '/structures' : '/accueil'
}

export default useHomePath
