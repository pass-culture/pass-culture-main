addonList.push(
  class PcTunnelHistory extends PcAddOn {
    static TUNNEL_SELECTORS = '.pc-tunnel-history .window'
    static MARGIN = 16

    bindEvents = () => {
      EventHandler.on(document.body, 'mousemove', PcTunnelHistory.TUNNEL_SELECTORS, this.#mousemove)
      EventHandler.on(window, 'resize', this.#resize)
      this.#resize()
    }

    unbindEvents = () => {
      EventHandler.off(document.body, 'mousemove', PcTunnelHistory.TUNNEL_SELECTORS, this.#mousemove)
      EventHandler.off(window, 'resize', this.#resize)
    }

    #resize = (event) => {
      document.querySelectorAll(PcTunnelHistory.TUNNEL_SELECTORS).forEach(
        ($window) => {
          // handle progress bar display with resize
          const $progress = $window.querySelector('.progress')
          $progress.style.width = 'auto'
          const $content = $window.querySelector('.content')
          $progress.style.width = ($content.scrollWidth - PcTunnelHistory.MARGIN) + 'px'
          // keep content in accepted positions
          let left = parseInt($content.style.left.substr(0, $content.style.left.length - 2))
          if (left > PcTunnelHistory.MARGIN) {
            left = PcTunnelHistory.MARGIN
            $content.style.left = left + 'px'
          } else if ((left + $content.scrollWidth) < ($window.clientWidth - PcTunnelHistory.MARGIN)){
            left = $window.clientWidth - PcTunnelHistory.MARGIN - $content.scrollWidth
            $content.style.left = left + 'px'
          }
        }
      )
    }

    #mousemove = (event) => {
      if (event.buttons == 1 ) {
        event.preventDefault()
        event.stopPropagation()
        const $window = event.target.closest('.window')
        const $content = event.target.closest('.content')
        if ($content != null){
          let left = parseInt($content.style.left.substr(0, $content.style.left.length - 2))
          left += event.movementX
          if (left <= PcTunnelHistory.MARGIN && (left + $content.scrollWidth) >= ($window.clientWidth - PcTunnelHistory.MARGIN)) {
            $content.style.left = left + 'px'
          }
        }
      }
    }
  }
)