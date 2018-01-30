/*
import {
  clientSignin as body,
  // professionalSignin as body
} from './mock'
import { requestData } from '../reducers/data'
*/
import { IS_DEV } from '../utils/config'

const init = store => {
  // mock sign
  if (IS_DEV) {
    /*
    store.dispatch(requestData(
      'POST',
      'users/signin',
      { body, key: 'users' }
    ))
    */
  }
}

export default init
