import React, { Component } from 'react'
import { ROOT_PATH } from '../utils/config';

class ProfilePicture extends Component {
  render() {
    return <img src={`${ROOT_PATH}/icons/ico-user-w@2x.png`} alt='Avatar' {...this.props}/>
  }
}

export default ProfilePicture
