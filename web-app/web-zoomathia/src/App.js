import './App.css';
import SearchComponent from './components/SearchComponent';
import Navbar from './components/page/Navbar';
import Footer from './components/page/Footer';
import Home from './components/page/Home';
import Work from './components/WorkComponent';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CompetencyQuestionComponent from './components/CompetencyQuestionComponent';
import ExplorerComponent from './components/ExploreComponent';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path='/' element={<Home />} />
        <Route index element={<Home />} />
        <Route path='ExploreAWork' element={<ExplorerComponent />} />
        <Route path='ExploreTheCorpus' element={<SearchComponent />} />
        <Route path='CompetencyQuestion' element={<CompetencyQuestionComponent />} />
        <Route path='Work' element={<Work />} />
      </Routes>
      <Footer />
    </BrowserRouter>

  );
}

export default App;
