import { memo, useEffect, useMemo, useRef } from 'react'

import flakeImage1 from './assets/flake1.png'
import flakeImage2 from './assets/flake2.png'
import flakeImage3 from './assets/flake3.png'
import flakeImage4 from './assets/flake4.png'
import styles from './SnowFlakes.module.scss'

const PI2 = Math.PI * 2
const randomBetween = (min: number, max: number) =>
  Math.random() * (max - min) + min
const computeMaxFlakes = () => Math.ceil(globalThis.innerWidth / 100)

const CANVAS_HEIGHT = 350
let NUMBER_OF_MAX_FLAKES = computeMaxFlakes() // Not a constant (may change on resize)
let CANVAS_WIDTH = globalThis.innerWidth // Not a constant (may change on resize)

const SnowFlakesComponent = (): JSX.Element => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const flakeImageRefs = useRef<HTMLImageElement[]>([])

  const flakeImages = useMemo(
    () => [flakeImage1, flakeImage2, flakeImage3, flakeImage4],
    []
  )

  const createFlake = useMemo(
    () => (id: number) => {
      const x = Math.random() * CANVAS_WIDTH
      const y = -Math.random() * CANVAS_HEIGHT
      const size = randomBetween(1, 50)
      const speedX = randomBetween(-size * 0.01, size * 0.01)
      const speedY = size * 0.01
      const opacity = 1 - y / CANVAS_HEIGHT
      const rotationSpeed = randomBetween(-PI2, PI2) * 0.003

      return {
        id,
        x,
        y,
        size,
        speedX,
        speedY,
        opacity,
        rotation: 0,
        rotationSpeed,
      }
    },
    []
  )

  const flakes = useMemo(() => {
    return Array.from({ length: NUMBER_OF_MAX_FLAKES }, (_, index) =>
      createFlake(index)
    )
  }, [createFlake])

  const updateFlakes = useMemo(() => {
    return () => {
      flakes.forEach((flake, index) => {
        flake.speedX += randomBetween(-0.01, 0.01)
        flake.x += Math.sin(flake.speedX)
        flake.y += flake.speedY
        flake.opacity = 1 - flake.y / CANVAS_HEIGHT
        flake.rotation += flake.rotationSpeed

        // Reposition flake if it goes out of the canvas
        const needsRespawnY = flake.y > CANVAS_HEIGHT
        const needsRespawnX = flake.x > CANVAS_WIDTH || flake.x + flake.size < 0

        if (needsRespawnY || needsRespawnX) {
          // Screen size may have changed and maybe we should remove or add some snowflakes to maintain balance
          if (flakes.length > NUMBER_OF_MAX_FLAKES) {
            flakes.splice(index, 1)
            return
          } else if (flakes.length < NUMBER_OF_MAX_FLAKES) {
            flakes[flakes.length] = createFlake(flakes.length)
          }

          if (needsRespawnY) {
            flake.y = -flake.size
            flake.x = Math.random() * CANVAS_WIDTH
          }
          if (needsRespawnX) {
            flake.x = flake.x > CANVAS_WIDTH ? 0 : CANVAS_WIDTH - flake.size
          }
        }
      })
    }
  }, [flakes, createFlake])

  const renderFlakes = useMemo(() => {
    return (canvas: HTMLCanvasElement, context: CanvasRenderingContext2D) => {
      context.clearRect(0, 0, canvas.width, canvas.height)

      flakes.forEach((flake) => {
        context.globalAlpha = flake.opacity
        context.save()
        context.translate(flake.x, flake.y)
        context.rotate(flake.rotation)
        context.drawImage(
          flakeImageRefs.current[
            flake.id % flakeImages.length
          ] as CanvasImageSource,
          -flake.size / 2,
          -flake.size / 2,
          flake.size,
          flake.size
        )
        context.restore()
        context.globalAlpha = 1
      })
    }
  }, [flakes, flakeImages.length])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) {
      return
    }

    const context = canvas.getContext('2d')

    const onResize = () => {
      NUMBER_OF_MAX_FLAKES = computeMaxFlakes()
      CANVAS_WIDTH = globalThis.innerWidth

      context?.save()
      canvas.width = CANVAS_WIDTH
      canvas.height = CANVAS_HEIGHT
      context?.restore()
    }
    globalThis.addEventListener('resize', onResize)
    onResize()

    let animationFrameId: number

    const animationLoop = () => {
      if (context) {
        updateFlakes()
        renderFlakes(canvas, context)
      }
      animationFrameId = requestAnimationFrame(animationLoop)
    }
    animationLoop()

    return () => {
      cancelAnimationFrame(animationFrameId)
      globalThis.removeEventListener('resize', onResize)
    }
  }, [updateFlakes, renderFlakes])

  return (
    <canvas className={styles['snow-flakes-canvas']} ref={canvasRef}>
      {flakeImages.map((flakeImage) => (
        <img
          key={flakeImage}
          src={flakeImage}
          ref={(el) => {
            if (el) {
              flakeImageRefs.current.push(el)
            }
          }}
          alt=""
        />
      ))}
    </canvas>
  )
}

export const SnowFlakes = memo(SnowFlakesComponent)
