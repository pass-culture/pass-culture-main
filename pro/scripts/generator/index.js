import { generateComponent } from './gen-component.js'
import { generateUtil } from './gen-util.js'

const ARGV = process.argv
  .slice(2)
  .map((arg) => (arg.startsWith('--') ? arg.slice(2) : arg))

;(async () => {
  try {
    console.log('') // Empty

    switch (ARGV[0].toLowerCase()) {
      case 'component':
        generateComponent(ARGV[1])
        break

      case 'util':
        generateUtil(ARGV[1])
        break

      default:
        console.log('Unknown command\nAborted!')
    }
  } catch (e) {
    console.log('Error', e.message)
  }
})()
