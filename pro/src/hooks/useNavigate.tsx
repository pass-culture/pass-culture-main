// it's not realy usefull to check that history is called.
// This will hook be removed on react-router-v6 migration
/* istanbul ignore file */
import { useHistory } from 'react-router'

interface INaviateFunction {
  (
    url: string,
    options?: {
      replace: boolean
    }
  ): void
}

const useNavigate = (): INaviateFunction => {
  const history = useHistory()
  return (url: string, options = { replace: false }) =>
    options.replace ? history.replace(url) : history.push(url)
}

export default useNavigate
