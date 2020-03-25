import React, { PureComponent } from 'react'
import lottie from 'lottie-web'
import animation from './animation.json'

class LoadingPage extends PureComponent {
  componentDidMount() {
    lottie.loadAnimation({
      container: document.getElementById('loading-animation'),
      renderer: 'svg',
      loop: true,
      autoplay: true,
      animationData: animation,
    })
  }

  render() {
    return (
      <div className="loading-page">
        <div id="loading-animation" />
        <p>
          {'Chargement en cours ...'}
        </p>
      </div>
    )
  }
}

export default LoadingPage
