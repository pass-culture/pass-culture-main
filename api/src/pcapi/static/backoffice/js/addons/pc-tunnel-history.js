addonList.push(
  class PcTunnelHistory extends PcAddOn {
    static TUNNEL_SELECTOR = '.pc-tunnel-history'
    static WINDOW_SELECTOR = '.window'
    static CONTENT_SELECTOR = '.content'
    static PROGRESS_SELECTOR = '.progress'
    static LEFT_SCROLL_SELECTOR = '.left-scroll'
    static RIGHT_SCROLL_SELECTOR = '.right-scroll'
    static AUTO_MOVE_DELAY = 16 // ms
    static AUTO_MOVE_DISTANCE = 16 // px
    static MARGIN = 16 // px

    bindEvents = () => {
      EventHandler.on(document.body, 'mousemove', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.WINDOW_SELECTOR, this.#mousemove)
      EventHandler.on(document.body, 'mousedown', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.LEFT_SCROLL_SELECTOR, this.#moveLeft)
      EventHandler.on(document.body, 'mousedown', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.RIGHT_SCROLL_SELECTOR, this.#moveRight)
      EventHandler.on(document.body, 'mouseup', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.LEFT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.on(document.body, 'mouseup', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.RIGHT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.on(document.body, 'mouseout', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.LEFT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.on(document.body, 'mouseout', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.RIGHT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.on(window, 'resize', this.#resize)
      this.#resize()
    }

    unbindEvents = () => {
      EventHandler.off(document.body, 'mousemove', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.WINDOW_SELECTOR, this.#mousemove)
      EventHandler.off(document.body, 'mousedown', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.LEFT_SCROLL_SELECTOR, this.#moveLeft)
      EventHandler.off(document.body, 'mousedown', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.RIGHT_SCROLL_SELECTOR, this.#moveRight)
      EventHandler.off(document.body, 'mouseup', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.LEFT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.off(document.body, 'mouseup', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.RIGHT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.off(document.body, 'mouseout', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.LEFT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.off(document.body, 'mouseout', PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.RIGHT_SCROLL_SELECTOR, this.#clearMove)
      EventHandler.off(window, 'resize', this.#resize)
    }

    #moveRight = (event) => {
      this.currentMove = {
        "content": event.target.closest(PcTunnelHistory.TUNNEL_SELECTOR).querySelector(PcTunnelHistory.CONTENT_SELECTOR),
        "window": event.target.closest(PcTunnelHistory.TUNNEL_SELECTOR).querySelector(PcTunnelHistory.WINDOW_SELECTOR),
        "distance": -PcTunnelHistory.AUTO_MOVE_DISTANCE,
        "id":  setInterval(this.#autoMove, PcTunnelHistory.AUTO_MOVE_DELAY) ,
      }
    }
    #moveLeft = (event) => {
      this.currentMove = {
        "content": event.target.closest(PcTunnelHistory.TUNNEL_SELECTOR).querySelector(PcTunnelHistory.CONTENT_SELECTOR),
        "window": event.target.closest(PcTunnelHistory.TUNNEL_SELECTOR).querySelector(PcTunnelHistory.WINDOW_SELECTOR),
        "distance": PcTunnelHistory.AUTO_MOVE_DISTANCE,
        "id":  setInterval(this.#autoMove, PcTunnelHistory.AUTO_MOVE_DELAY) ,
      }
    }

    #clearMove = (event) => {
      if (!! this.currentMove) {
        clearInterval(this.currentMove.id)
        this.currentMove = undefined
      }
    }

    #resize = (event) => {
      document.querySelectorAll(PcTunnelHistory.TUNNEL_SELECTOR + ' ' + PcTunnelHistory.WINDOW_SELECTOR).forEach(
        ($window) => {
          // handle progress bar display with resize
          const $progress = $window.querySelector(PcTunnelHistory.PROGRESS_SELECTOR)
          const $content = $window.querySelector(PcTunnelHistory.CONTENT_SELECTOR)
          if (!!$progress) {
            $progress.style.width = 'auto'
            $progress.style.width = ($content.scrollWidth - PcTunnelHistory.MARGIN) + 'px'
          }
          // keep content in accepted positions
          let left = this.#extractLeftValue($content)
          this.#applyLeftValue($window, $content, left)
        }
      )
    }

    #mousemove = (event) => {
      if (event.buttons == 1 ) {
        event.preventDefault()
        event.stopPropagation()
        const $window = event.target.closest(PcTunnelHistory.WINDOW_SELECTOR)
        const $content = event.target.closest(PcTunnelHistory.CONTENT_SELECTOR)
        if ($content != null){
          let left = this.#extractLeftValue($content)
          left += event.movementX
          this.#applyLeftValue($window, $content, left)
        }
      }
    }

    #autoMove = () => {
      if (!! this.currentMove) {
        const $content = this.currentMove.content
        const $window = this.currentMove.window
        const left = this.#extractLeftValue($content) + this.currentMove.distance
         if (!this.#applyLeftValue($window, $content, left)){
          this.#clearMove()
         }
      }
    }

    #applyLeftValue = ($window, $content, left) => {
      const minLeft = $window.clientWidth - $content.scrollWidth
      if (minLeft === 0) {
        // content is the same size as the window
        $window.previousElementSibling.classList.add('text-white')
        $window.nextElementSibling.classList.add('text-white')
        $content.style.left = '0px'
        return false
      } else if (left >= 0){
        $content.style.left = '0px'
        $window.previousElementSibling.classList.add('text-white')
        $window.nextElementSibling.classList.remove('text-white')
        return false
      } else if (left <= minLeft) {
        $content.style.left = minLeft + 'px'
        $window.previousElementSibling.classList.remove('text-white')
        $window.nextElementSibling.classList.add('text-white')
        return false
      } else {
        $content.style.left = left + 'px'
        $window.previousElementSibling.classList.remove('text-white')
        $window.nextElementSibling.classList.remove('text-white')
        return true
      }
    }

    #extractLeftValue = ($content) => {
      return parseInt($content.style.left.substr(0, $content.style.left.length - 2))
    }
  }
)