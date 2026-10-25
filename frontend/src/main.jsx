import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/overpass'
import './index.css'
import './styles/tokens.css'
import './styles/app.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
