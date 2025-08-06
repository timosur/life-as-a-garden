import { Routes, Route } from 'react-router-dom'
import './App.css'
import CanvasGarden from './components/CanvasGarden'
import Notes from './components/Notes'
import Edit from './components/Edit'

function App() {
  return (
    <main className="app-content">
      <Routes>
        <Route path="/" element={<CanvasGarden />} />
        <Route path="/notes" element={<Notes />} />
        <Route path="/edit" element={<Edit />} />
      </Routes>
    </main>
  )
}

export default App
