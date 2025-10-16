import { useSelector } from 'react-redux'

import type { RootState } from '../store/store'

// https://react-redux.js.org/using-react-redux/usage-with-typescript#define-typed-hooks
export const useAppSelector = useSelector.withTypes<RootState>()
