import { Routes, Route } from 'react-router-dom'
import './App.css'
import CanvasGarden from './components/CanvasGarden'
import Notes from './components/Notes'
import Edit from './components/Edit'
import { Calendar } from './components/Calendar'

function App() {
  return (
    <main className="app-content">
      <Routes>
        <Route path="/" element={<CanvasGarden />} />
        <Route path="/notes" element={<Notes />} />
        <Route path="/edit" element={<Edit />} />
        <Route path="/calendar" element={<Calendar />} />
      </Routes>
    </main>
  )
}

export default App
