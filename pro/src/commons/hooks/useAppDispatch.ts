import { useDispatch } from 'react-redux'

import type { AppDispatch } from '../store/store'

// https://react-redux.js.org/using-react-redux/usage-with-typescript#define-typed-hooks
export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
