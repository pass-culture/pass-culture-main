// it's not realy usefull to check that history is called.
// This will hook be removed on react-router-v6 migration
/* istanbul ignore file */
import { useHistory } from 'react-router'

interface INavigateFunction {
  (
    url: string,
    options?: {
      replace: boolean
    },
    search?: string
  ): void
}

const useNavigate = (): INavigateFunction => {
  const history = useHistory()
  return (url: string, options = { replace: false }, search) =>
    options.replace
      ? history.replace(url)
      : history.push({ pathname: url, search: search })
}

export default useNavigate
