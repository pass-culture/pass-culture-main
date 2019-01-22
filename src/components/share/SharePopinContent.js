/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { Transition } from 'react-transition-group'

import { closeSharePopin } from '../../reducers/share'

const transitionDelay = 500
const transitionDuration = 250

const defaultStyle = {
  transitionDuration: `${transitionDuration}ms`,
  transitionProperty: 'bottom',
  transitionTimingFunction: 'ease',
}

const transitionStyles = {
  entered: { bottom: 0, opacity: 1 },
  entering: { bottom: '-100%', opacity: 1 },
  exited: { bottom: '-100%', opacity: 0 },
  exiting: { bottom: '-100%', opacity: 0 },
}

class SharePopinContent extends React.PureComponent {
  closeHandler = () => {
    const { dispatch } = this.props
    dispatch(closeSharePopin())
  }

  renderCloseButton = () => (
    <button
      type="button"
      id="share-popin-close-button"
      className="pc-text-button is-absolute fs16"
      onClick={this.closeHandler}
    >
      <span
        aria-hidden
        className="icon-legacy-close is-white-text"
        title="Fermer la popin de partage"
      />
    </button>
  )

  render() {
    const { visible, options } = this.props
    const { text, title } = options
    return (
      <Transition in={visible} timeout={transitionDelay}>
        {status => (
          <div
            id="share-popin"
            className={`is-absolute mx6 mt6 transition-${status}`}
            style={{ ...defaultStyle, ...transitionStyles[status] }}
          >
            {options && (
              <div className="pc-theme-gradient inner is-relative is-clipped">
                {this.renderCloseButton()}
                <div
                  id="share-popin-fixed-container"
                  className="fs16 text-left"
                >
                  <div className="ml24 mr48 mt20 mb32">
                    {/* <!-- Popin event text --> */}
                    <h3>
                      <span className="is-bold">{title}</span>
                    </h3>
                    <p className="mt18">
                      {/* <!-- Popin status text --> */}
                      <span>{text}</span>
                    </p>
                  </div>
                  <div className="dotted-top-white flex-columns flex-around">
                    {/* <!-- Popin buttons --> */}
                    {options.buttons}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </Transition>
    )
  }
}

SharePopinContent.propTypes = {
  dispatch: PropTypes.func.isRequired,
  options: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
  visible: PropTypes.bool.isRequired,
}

export default SharePopinContent
