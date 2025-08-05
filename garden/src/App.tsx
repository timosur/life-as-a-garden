import { Routes, Route } from 'react-router-dom'
import './App.css'
import CanvasGarden from './components/CanvasGarden'
import Notes from './components/Notes'

function App() {
  return (
    <main className="app-content">
      <Routes>
        <Route path="/" element={<CanvasGarden />} />
        <Route path="/notes" element={<Notes />} />
      </Routes>
    </main>
  )
}

export default App
