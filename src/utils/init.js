import {
  // clientSignin as body,
  professionalSignin as body
} from './mock'
import { requestData } from '../reducers/data'
import { IS_DEV } from '../utils/config'

const init = store => {
  // mock sign
  console.log("IS_DEV: ", IS_DEV)
  if (IS_DEV) {
    store.dispatch(requestData(
      'POST',
      'signin',
      { body, key: 'users' }
    ))
  }
}

export default init
