import { BrowserRouter as Router, Routes, Route} from "react-router-dom";
import './App.css'
import DatasetData from './assets/dataset_data'

function App() {
 
  return (
    <Router> 
      <Routes>
        <Route exact path="/" element={<DatasetData/>} />
      </Routes>
  </Router>
  )
}

export default App
